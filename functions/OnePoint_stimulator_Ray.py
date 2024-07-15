from neuron import h, gui
import numpy as np
import matplotlib.pyplot as plt
from neuron.units import ms, mV, um
import plotly
import plotly.graph_objects as go
from functions import Load_neuron
import ray

# Initialize Ray
ray.init(num_cpus=8, num_gpus=4)

soma, axon_list, apic_list, dend_list = Load_neuron.load_neuron()

@ray.remote
class One_point:
    # def OnePoint_TI_wave has two functions(TI wave generation and Action potential generation)
    # 1. TI wave generation
    # 2. Action potential generation for checking conduction block
    def OnePoint_TI_wave(location, amp1_1, amp1_2, freq1, freq2, delay, dur, end, imp_am, imp_location, sp_rate):
        # 1. TI wave generation
        # Generate the time array and sine wave
        #dt = 0.001  # Time step size (in ms)
        duration = delay + dur
        end_time = duration + end
        sampling_rate =  sp_rate #1 / (freq1 * 16)  # Sampling rate
        stim_t = np.arange(0, duration, sampling_rate)  # Time array
        # pluswave generate
        plus_wave_1 = amp1_1 * np.sin(2 * np.pi * freq1 * stim_t / 1000) # s to ms
        plus_wave_2 = amp1_2 * np.sin(2 * np.pi * freq2 * stim_t / 1000)
        plus_wave = plus_wave_1 + plus_wave_2

        # preprocessing
        d = delay / (sampling_rate)
        plus_wave[0: int(d)] = 0
        temp = np.zeros(int((end_time - duration)/sampling_rate))
        plus_wave = np.append(plus_wave, temp)
        stim_t = np.append(stim_t, np.arange(duration, end_time, sampling_rate))

        # 2. Action potential generation
        # This will stimulate the start point of the axon (in this case, axon0)
        temp2 = np.arange(0, end_time, sampling_rate)
        impulse = np.where(temp2 == imp_location, imp_am, 0)

        def TI_result(location, delay, duration, sampling_rate, end_time, stim_t, plus_wave, impulse):
            # Insert a current clamp (IClamp) at the location
            iclamp = h.IClamp(location)
            ap_generate = h.IClamp(axon_list[0](0))

            # Create a NEURON Vector for the sine wave
            stim_vector2 = h.Vector(plus_wave.tolist())
            stim_vector3 = h.Vector(impulse.tolist())

            # Assign the sine wave as the current waveform using the Vector.play() method
            iclamp.delay = delay  # Start injecting immediately
            iclamp.dur = duration  # Duration of the injection
            iclamp.amp = 0  # Set the initial amplitude to 0
            stim_vector2.play(iclamp._ref_amp, sampling_rate)

            # Assign the test pulse
            ap_generate.delay = delay
            ap_generate.dur = duration
            ap_generate.amp = 0
            stim_vector3.play(ap_generate._ref_amp, sampling_rate)

            # Run the simulation
            h.dt = sampling_rate  # Set the integration time step
            h.tstop = duration  # Set the simulation duration
            h.run()

            t = h.Vector().record(h._ref_t)
            # record the results
            # You can see other section of results. The below is format. Plz change only {} part.
            # h.Vector().record({the sectioin you want}._ref_v)
            axon0_v_9 = h.Vector().record(axon_list[0](0.9)._ref_v)
            axon5_v = h.Vector().record(axon_list[5](0.8)._ref_v)
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
            fig_r.add_trace(go.Scatter(x=[], y=[], name="axon0_9", mode='lines', line=dict(width=1)))
            fig_r.add_trace(go.Scatter(x=[], y=[], name="axon5_v", mode='lines', line=dict(width=1)))

            axon5_v = np.array(axon5_v)
            axon0_v_9 = np.array(axon0_v_9)
            # Use the generator to plot data in chunks
            generator = plot_data_generator(stim_t, plus_wave, axon0_v_9, axon5_v, chunk_size)

            for time_chunk, wave_chunk, axon0_v_9_chunk, axon5_v in generator:
                fig_r.data[0].x = np.append(fig_r.data[0].x, time_chunk)
                fig_r.data[0].y = np.append(fig_r.data[0].y, wave_chunk)
                fig_r.data[1].x = np.append(fig_r.data[1].x, time_chunk)
                fig_r.data[1].y = np.append(fig_r.data[1].y, axon0_v_9_chunk)
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

        TI_result(location, delay, duration, sampling_rate, end_time, stim_t, plus_wave, impulse)