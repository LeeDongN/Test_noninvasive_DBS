from neuron import h, gui
import numpy as np
from neuron.units import ms, mV, um
import plotly
import plotly.graph_objects as go
from functions import Load_neuron

soma, axon_list, apic_list, dend_list = Load_neuron.load_neuron()

# Several points stimulation functioin
class Several_potins:

    # def TI_wave has two functions(TI wave generation and Action potential generation)
    # 1. TI wave generation
    # 2. Action potential generation for checking conduction block
    def SeveralPoints_TI_wave(amp1_1, amp1_2, freq1, freq2, delay, dur, end, imp_am, imp_location, seg_length):
        # 1. TI wave generation
        # Generate the time array and sine wave
        dt = 0.001  # Time step size (in ms)
        duration = delay + dur  # how much stimulate
        end_time = duration + end  # end time
        stim_t = np.arange(0, duration, dt)  # Time array
        # Making TI waves
        plus_wave_1 = amp1_1 * np.sin(2 * np.pi * freq1 * stim_t / 1000)
        plus_wave_2 = amp1_2 * np.sin(2 * np.pi * freq2 * stim_t / 1000)
        plus_wave = plus_wave_1 + plus_wave_2
        # Preprocessing of TI wave
        # fill 0 before the stimulation time
        d = delay/dt
        plus_wave[0: int(d)] = 0
        temp = np.zeros(int((end_time-duration)/dt))
        plus_wave = np.append(plus_wave, temp)
        stim_t = np.append(stim_t, np.arange(duration, end_time, dt))

        # 2. Action potential generation
        # This will stimulate the start point of the axon (in this case, axon0)
        temp2 = np.arange(0, end_time, dt)
        # control the time when inject the action potential generation (in this case, imp_location is the time to generate action potential)
        impulse = np.where(temp2 == imp_location, imp_am, 0)

        # Simulation part
        def several_result():
            # First, we assigned current stimulator(iClamp) on whole sections
            # axon iClamp
            num = 0
            for m in axon_list:
                # devide the subsection of axon with seg_length.
                # it means the subsection will be devided and iClamp will be attached on each subsubsection.
                # For example, if the length of the subsection is 100um and seg_length is 10um,
                # the iClamp will be attached every 10 um of the subsection.
                nseg = round(m.L/seg_length)
                for k in range(1, nseg):
                    globals()['AM_{}'.format(str(m)[0:4]) +
                              '{}'.format(num) + '_{}'.format(k)] = h.IClamp(m(k/nseg))
                num = num + 1
            # dend iclamp
            num = 0
            for m in dend_list:
                nseg = round(m.L/seg_length)
                for k in range(1, nseg):
                    globals()['AM_{}'.format(str(m)[0:4]) +
                              '{}'.format(num) + '_{}'.format(k)] = h.IClamp(m(k/nseg))
                num = num + 1
            # apicla iclamp
            num = 0
            for m in apic_list:
                nseg = round(m.L/seg_length)
                for k in range(1, nseg):
                    globals()['AM_{}'.format(str(m)[0:4]) +
                              '{}'.format(num) + '_{}'.format(k)] = h.IClamp(m(k/nseg))
                num = num + 1
            # soma iclamp
            for k in range(1, 3):
                globals()['AM_soma_{}'.format(k)] = h.IClamp(soma(k/3))

            # Action potential generation for checking conduction block
            # injected current on the first section of axon
            ap_generate = h.IClamp(axon_list[0](0))

            # Create a NEURON Vector for the sine wave
            AM_vector = h.Vector(plus_wave.tolist())
            impulse_vector = h.Vector(impulse.tolist())

            # Assign the properties of iclamp
            num = 0
            for m in axon_list:
                nseg = round(m.L/seg_length)
                for k in range(1, nseg):
                    eval('AM_{}'.format(
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k)).delay = delay
                    eval('AM_{}'.format(
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k)).dur = duration
                    eval('AM_{}'.format(
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k)).amp = 0
                    AM_vector.play(eval('AM_{}'.format(
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k))._ref_amp, dt)
                num = num + 1
            num = 0
            for m in apic_list:
                nseg = round(m.L/seg_length)
                for k in range(1, nseg):
                    eval('AM_{}'.format(
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k)).delay = delay
                    eval('AM_{}'.format(
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k)).dur = duration
                    eval('AM_{}'.format(
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k)).amp = 0
                    AM_vector.play(eval('AM_{}'.format(
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k))._ref_amp, dt)
                num = num + 1
            num = 0
            for m in dend_list:
                nseg = round(m.L/seg_length)
                for k in range(1, nseg):
                    eval('AM_{}'.format(
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k)).delay = delay
                    eval('AM_{}'.format(
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k)).dur = duration
                    eval('AM_{}'.format(
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k)).amp = 0
                    AM_vector.play(eval('AM_{}'.format(
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k))._ref_amp, dt)
                num = num + 1
            num = 0
            for k in range(1, 3):
                eval('AM_soma' + '_' + str(k)).delay = delay
                eval('AM_soma' + '_' + str(k)).dur = duration
                eval('AM_soma' + '_' + str(k)).amp = 0
                AM_vector.play(eval('AM_soma' + '_' + str(k))._ref_amp, dt)

            # Assign the test pulse
            ap_generate.delay = delay
            ap_generate.dur = duration
            ap_generate.amp = 0
            impulse_vector.play(ap_generate._ref_amp, dt)

            # Run the simulation
            h.dt = dt  # Set the integration time step
            h.tstop = duration  # Set the simulation duration
            h.run()

            # record the results
            # You can see other section of results. The below is format. Plz change only {} part.
            # h.Vector().record({the sectioin you want}._ref_v)
            t = h.Vector().record(h._ref_t)
            axon0_v_8 = h.Vector().record(axon_list[0](0.8)._ref_v)
            axon5_v_8 = h.Vector().record(axon_list[5](0.8)._ref_v)
            # the resting potential
            h.finitialize(-65*mV)
            h.continuerun(end_time)

            # making figure
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatter(
                x=stim_t, y=AM_vector, name="injected AM wave"))
            fig_r.add_trace(go.Scatter(x=t, y=axon5_v_8,
                            name="axon(5)_v", line=dict(color="#DA5A2A")))
            fig_r.add_trace(go.Scatter(x=temp2, y=impulse,
                                       mode='lines', name="impulse"))
            fig_r.add_trace(go.Scatter(x=t, y=axon0_v_8,
                            name="axon(0_8)_v", line=dict(color="#3B1877")))
            
            fig_r.update_layout(
                width=800,
                yaxis_title="membrane potential (mV)",
                xaxis_title="Time (ms)",
                xaxis_range=[0, end_time],
                plot_bgcolor='white'
            )
            fig_r.update_xaxes(
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )
            fig_r.update_yaxes(
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )
            fig_r.show()

        several_result()