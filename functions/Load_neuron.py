from neuron import h, gui

def load_neuron():
    # load neuron model
    h.load_file('C:/Workspace/NEURON/Noninvasive_DBS2/Neuron_model.ses')

    # The neuron model has several sections(in this case, Soma, Axon, Apic, Dendrite)
    # And each section has several subsections
    axon_list = []
    apic_list = []
    dend_list = []
    soma = h.soma

    # append each section in the list
    for i in range(0, 7):
        axon_list.append(h.axon[i])
    for i in range(0, 29):
        apic_list.append(h.apic[i])
    for i in range(0, 29):
        dend_list.append(h.dend[i])
    
    return soma, axon_list, apic_list, dend_list
