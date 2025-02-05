import angr
import claripy

FLAG_LEN = 35

project = angr.Project("./flag_checker", main_opts={'base_addr': 0x400000}, auto_load_libs=False)


flag_chars = [claripy.BVS('flag_%d' % i, 8) for i in range(FLAG_LEN)]
flag = claripy.Concat( *flag_chars + [claripy.BVV(b'\n')]) # Add \n for scanf() to accept the input

state = project.factory.full_init_state(
        args=['./flag_checker'],
        add_options=angr.options.unicorn,
        stdin=flag,
)

for k in flag_chars:
    state.solver.add(k >= ord('!'))
    state.solver.add(k <= ord('~'))

sm = project.factory.simulation_manager(state)

good_address = 0x00401391   # Endereço correto
avoid_address = 0x0040139b  # Endereço incorreto

sm.explore(find=good_address, avoid=avoid_address)

print(sm)
print(sm.found[0].posix.dumps(0))
