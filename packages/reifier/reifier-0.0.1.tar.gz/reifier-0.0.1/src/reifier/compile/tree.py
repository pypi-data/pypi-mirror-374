from dataclasses import dataclass, field
from collections.abc import Callable
from typing import Any

from reifier.compile.levels import Levels, Level, Origin, Parent
from reifier.compile.blocks import Block, BlockTracer, traverse
# from circuits.neurons.core import Bit
# from circuits.compile.monitor import find


@dataclass(frozen=True)
class Tree(Levels):
    """A tree representation of a function"""

    # TODO: reform as a separate class with .levels property
    root: Block
    origin_blocks: list[list[Block]]

    @classmethod
    def from_root(cls, root: Block) -> "Tree":
        origin_blocks = cls.set_origins(root)
        cls.set_narrow_origins(origin_blocks)
        levels = [Level(tuple([b.origin for b in level])) for level in origin_blocks]
        return cls(root=root, origin_blocks=origin_blocks, levels=tuple(levels))

    @staticmethod
    def set_origins(root: Block) -> list[list[Block]]:
        depth = root.top
        levels: list[list[Block]] = [[] for _ in range(depth)]

        # Set connections and add to levels
        for b in traverse(root):
            if b.flavour == "gate" or b.flavour == "folded":
                out = b.creation.data
                weights_in = out.source.weights
                bias = out.source.bias
                if b.flavour == "folded":
                    bias += b.origin.bias
            elif b.flavour == "copy":
                weights_in = [1]
                bias = -1
            else:
                continue
            indices_in = [
                inp.creator.abs_x for inp in b.inputs if inp.creator is not None
            ]
            incoming = [Parent(idx, int(w)) for idx, w in zip(indices_in, weights_in)]
            b.origin = Origin(b.abs_x, tuple(incoming), int(bias))
            levels[b.abs_y].append(b)

        # set correct w for connections to inputs
        for j, b in enumerate(levels[1]):
            # assumes that all levels[0] inputs are root inputs, and that other levels have no such inputs
            # without this, gates on this level have [], [] for indices and w
            origin = b.origin
            incoming = [
                Parent(inp.creator.abs_x, 1)
                for inp in b.inputs
                if inp.creator is not None
            ]
            b.origin = Origin(origin.index, tuple(incoming), origin.bias)

        # set origins for inputs
        input_blocks: list[Block] = []
        assert len(levels[0]) == 0
        for b in traverse(root):
            if b.flavour == "input":
                input_blocks.append(b)
        levels[0] = input_blocks
        for j, b in enumerate(levels[0]):
            b.origin = Origin(j, (), -1)

        # set origins for outputs
        for j, out in enumerate(root.outputs):
            b = out.creator
            assert b is not None
            incoming = [
                Parent(inp.creator.abs_x, 1)
                for inp in b.inputs
                if inp.creator is not None
            ]
            b.origin = Origin(j, tuple(incoming), -1)
            levels[-1].append(b)

        if len(root.outputs) == 0:
            print("Warning, no outputs detected in the compiled function")
        if len(input_blocks) == 0:
            print("Warning, no inputs detected in the compiled function")

        return levels

    @staticmethod
    def set_narrow_origins(origin_blocks: list[list[Block]]) -> None:
        # record narrow indices
        to_narrow_index: dict[tuple[int, int], int] = dict()
        for i, level in enumerate(origin_blocks):
            for j, b in enumerate(level):
                to_narrow_index[(i, b.origin.index)] = j

        # set narrow indices
        for i, level in enumerate(origin_blocks[1:], start=1):  # skip input level
            for j, b in enumerate(level):
                origin = b.origin
                try:
                    index = to_narrow_index[(i, b.origin.index)]
                    incoming = [
                        Parent(to_narrow_index[(i - 1, p.index)], p.weight)
                        for p in origin.incoming
                    ]
                except KeyError:
                    raise KeyError(f"KeyError when setting narrow origins for {b.path}")
                b.origin = Origin(index, tuple(incoming), origin.bias)


    def print_activations(self) -> None:
        for i, level in enumerate(self.origin_blocks):
            level_activations = [b.creation.data.activation for b in level]
            print(i, "".join(str(int(a)) for a in level_activations))


    # def run(inputs: list[Bit]) -> list[Bit]:
    #     # TODO: implement
    #     pass


@dataclass(frozen=True)
class Compiler:
    collapse: set[str] = field(default_factory=set[str])

    def validate(self, args: Any, kwargs: Any) -> None:
        if "gate" in self.collapse:
            raise ValueError("gate cannot be collapsed")
        # dummy_inp = find(kwargs, Bit)
        # for bit, _ in dummy_inp:
        #     if bit.activation != 0:
        #         print("Warning: Dummy input has non-zero values")
        #         break

    def run(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Tree:
        """Compiles a function into a tree."""
        self.validate(args, kwargs)


        tracer = BlockTracer(self.collapse)
        root = tracer.run(fn, *args, **kwargs)
        tree = Tree.from_root(root)
        return tree
