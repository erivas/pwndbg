#!/usr/bin/env python
# -*- coding: utf-8 -*-
import capstone
import pwndbg.chain
import pwndbg.color
import pwndbg.disasm.jump

capstone_branch_groups = set((
capstone.CS_GRP_CALL,
capstone.CS_GRP_JUMP
))

def instruction(ins):
    asm = u'%-06s %s' % (ins.mnemonic, ins.op_str)

    branch = set(ins.groups) & capstone_branch_groups

    # tl;dr is a branch?
    if ins.target not in (None, ins.address + ins.size):
        sym    = pwndbg.symbol.get(ins.target)
        target = pwndbg.color.get(ins.target)
        const  = ins.target_constant

        # If it's a constant expression, color it directly in the asm.
        if const and const != 0:
            asm = asm.replace(hex(ins.target), target)

            if sym:
                asm = '%-36s <%s>' % (asm, sym)

        # It's not a constant expression, but we've calculated the target
        # address by emulation.
        elif sym:
            asm = '%-36s <%s; %s>' % (asm, target, sym)

        # We were able to calculate the target, but there is no symbol
        # name for it.
        else:
            asm = '%-36s <%s>' % (asm, target)

    # not a branch
    elif ins.symbol:
        if branch and not ins.target:
            asm = '%s <%s>' % (asm, ins.symbol)

            # XXX: not sure when this ever happens
            asm += '<-- file a pwndbg bug for this'
        else:
            colored_addr = pwndbg.color.get(ins.symbol_addr)
            asm = asm.replace(hex(ins.symbol_addr), ins.symbol)
            asm = '%-36s <%s>' % (asm, pwndbg.color.get(ins.symbol_addr))

    # Make the instruction mnemonic bold if it's a branch instruction.
    if branch:
        asm = asm.replace(ins.mnemonic, pwndbg.color.bold(ins.mnemonic))

    # If we know the conditional is taken, mark it as green.
    if ins.condition:
        asm = pwndbg.color.green(u'✔ ') + asm
    else:
        asm = '  ' + asm

    return asm
