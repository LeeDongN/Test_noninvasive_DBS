from functions import Load_neuron

soma, axon_list, apic_list, dend_list = Load_neuron.load_neuron()
# saving whole length of each sections (and subsections)
axon_L = []
apic_L = []
dend_L = []

for m in axon_list:
    axon_L.append(m.L)
for m in apic_list:
    apic_L.append(m.L)
for m in dend_list:
    dend_L.append(m.L)

class changing_R_L:
    def L_times(times):
        for m in axon_list:
            m.L = m.L*times
        for m in dend_list:
            m.L = m.L*times
        for m in apic_list:
            m.L = m.L*times

    def R_times(times):
        for m in axon_list:
            m.Ra = m.Ra*times
        for m in dend_list:
            m.Ra = m.Ra*times
        for m in apic_list:
            m.Ra = m.Ra*times
        soma.Ra = soma.Ra*times

    def R_reset():
        for m in axon_list:
            m.Ra = 70
        for m in dend_list:
            m.Ra = 70
        for m in apic_list:
            m.Ra = 70
        soma.Ra = 70

    def L_Reset():
        num = 0
        for m in axon_list:
            m.L = axon_L[num]
            num = num + 1
        num = 0
        for m in dend_list:
            m.L = dend_L[num]
            num = num + 1
        num = 0
        for m in apic_list:
            m.L = apic_L[num]
            num = num + 1