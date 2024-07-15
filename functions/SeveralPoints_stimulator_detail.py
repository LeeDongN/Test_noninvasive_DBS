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
    def SeveralPoints_TI_wave(amp1_1, amp1_2, freq1, freq2, delay, dur, end, imp_am, imp_location, seg_length, sp_rate):
        # 1. TI wave generation
        # Generate the time array and sine wave
        sampling_rate = sp_rate 
        duration = delay + dur  # how much stimulate
        end_time = duration + end  # end time
        stim_t = np.arange(0, duration, sampling_rate)  # Time array
        # Making TI waves
        plus_wave_1 = amp1_1 * np.sin(2 * np.pi * freq1 * stim_t / 1000)
        plus_wave_2 = amp1_2 * np.sin(2 * np.pi * freq2 * stim_t / 1000)
        plus_wave = plus_wave_1 + plus_wave_2
        # Preprocessing of TI wave
        # fill 0 before the stimulation time
        d = delay / sampling_rate
        plus_wave[0: int(d)] = 0
        temp = np.zeros(int((end_time-duration)/sampling_rate))
        plus_wave = np.append(plus_wave, temp)
        stim_t = np.append(stim_t, np.arange(duration, end_time, sampling_rate))

        # 2. Action potential generation
        # This will stimulate the start point of the axon (in this case, axon0)
        temp2 = np.arange(0, end_time, sampling_rate)
        # control the time when inject the action potential generation (in this case, imp_location is the time to generate action potential)
        impulse = np.where(temp2 == imp_location, imp_am, 0)

        # Simulation part
        def several_result(delay, duration, sampling_rate, end_time, stim_t, plus_wave, impulse, seg_length):
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
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k))._ref_amp, sampling_rate)
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
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k))._ref_amp, sampling_rate)
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
                        str(m)[0:4]) + '{}'.format(num) + '_' + str(k))._ref_amp, sampling_rate)
                num = num + 1
            num = 0
            for k in range(1, 3):
                eval('AM_soma' + '_' + str(k)).delay = delay
                eval('AM_soma' + '_' + str(k)).dur = duration
                eval('AM_soma' + '_' + str(k)).amp = 0
                AM_vector.play(eval('AM_soma' + '_' + str(k))._ref_amp, sampling_rate)

            # Assign the test pulse
            ap_generate.delay = delay
            ap_generate.dur = duration
            ap_generate.amp = 0
            impulse_vector.play(ap_generate._ref_amp, sampling_rate)

            # Run the simulation
            h.dt = sampling_rate  # Set the integration time step
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

            # Define a generator function to yield chunks of the data
            def plot_data_generator(time, wave, axon0_v_9, axon5_v, chunk_size):
                for i in range(0, len(time), chunk_size):
                    yield time[i:i + chunk_size], wave[i:i + chunk_size], axon0_v_9[i:i + chunk_size], axon5_v[i:i + chunk_size]

            # Define the chunk size for the generator
            chunk_size = 1000  # Adjust based on your memory constraints

            # Initialize the plotly figure with initial empty traces
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatter(x=[], y=[], name="Combined Wave", mode='lines', line=dict(width=1)))
            fig_r.add_trace(go.Scatter(x=[], y=[], name="axon0_9", mode='lines', line=dict(width=1, color="#3B1877")))
            fig_r.add_trace(go.Scatter(x=[], y=[], name="axon5_v", mode='lines', line=dict(width=1, color="#DA5A2A")))

            axon5_v_8 = np.array(axon5_v_8)
            axon0_v_8 = np.array(axon0_v_8)
            # Use the generator to plot data in chunks
            generator = plot_data_generator(stim_t, plus_wave, axon0_v_8, axon5_v_8, chunk_size)

            for time_chunk, wave_chunk, axon0_v_8_chunk, axon5_v in generator:
                fig_r.data[0].x = np.append(fig_r.data[0].x, time_chunk)
                fig_r.data[0].y = np.append(fig_r.data[0].y, wave_chunk)
                fig_r.data[1].x = np.append(fig_r.data[1].x, time_chunk)
                fig_r.data[1].y = np.append(fig_r.data[1].y, axon0_v_8_chunk)
                fig_r.data[2].x = np.append(fig_r.data[2].x, time_chunk)
                fig_r.data[2].y = np.append(fig_r.data[2].y, axon5_v)
            
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

        several_result(delay, duration, sampling_rate, end_time, stim_t, plus_wave, impulse, seg_length)