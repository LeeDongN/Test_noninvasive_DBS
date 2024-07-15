from neuron import h, gui
import numpy as np
import matplotlib.pyplot as plt
from neuron.units import ms, mV, um
import plotly
import plotly.graph_objects as go
from functions import Load_neuron

soma, axon_list, apic_list, dend_list = Load_neuron.load_neuron()

class One_point:
    # def OnePoint_TI_wave has two functions(TI wave generation and Action potential generation)
    # 1. TI wave generation
    # 2. Action potential generation for checking conduction block
    def OnePoint_TI_wave(location, amp1_1, amp1_2, freq1, freq2, delay, dur, end, imp_am, imp_location):
        # 1. TI wave generation
        # Generate the time array and sine wave
        dt = 1e-3  # Time step size (in ms)
        dt_ns = 1e-6
        duration = delay + dur
        end_time = duration + end
        stim_t = np.arange(0, duration, dt)  # Time array
        # pluswave generate
        plus_wave_1 = amp1_1 * np.sin(2 * np.pi * freq1 * stim_t / 1e6)
        plus_wave_2 = amp1_2 * np.sin(2 * np.pi * freq2 * stim_t / 1e6)
        plus_wave = plus_wave_1 + plus_wave_2

        # preprocessing
        d = delay/dt
        plus_wave[0: int(d)] = 0
        temp = np.zeros(int((end_time-duration)/dt))
        plus_wave = np.append(plus_wave, temp)
        stim_t = np.append(stim_t, np.arange(duration, end_time, dt)) # 원래는 dt_ns를 대입해야 함

        # 2. Action potential generation
        # This will stimulate the start point of the axon (in this case, axon0)
        temp2 = np.arange(0, end_time, dt)
        impulse = np.where(temp2 == imp_location, imp_am, 0)

        def TI_result(location, delay, duration, dt, end_time, stim_t, plus_wave, impulse):
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
            stim_vector2.play(iclamp._ref_amp, dt)

            # Assign the test pulse
            ap_generate.delay = delay
            ap_generate.dur = duration
            ap_generate.amp = 0
            stim_vector3.play(ap_generate._ref_amp, dt)

            # Run the simulation
            h.dt = dt  # Set the integration time step
            h.tstop = duration  # Set the simulation duration
            h.run()

            t = h.Vector().record(h._ref_t)
            # record the results
            # You can see other section of results. The below is format. Plz change only {} part.
            # h.Vector().record({the sectioin you want}._ref_v)
            axon0_v_9 = h.Vector().record(axon_list[0](0.9)._ref_v)
            axon5_v_9 = h.Vector().record(axon_list[5](0.8)._ref_v)
            h.finitialize(-65*mV)
            h.continuerun(end_time)

            fig_r = go.Figure()
            fig_r.add_trace(go.Scatter(
                x=temp2, y=impulse, name="AP_generator"))
            fig_r.add_trace(go.Scatter(
                x=stim_t, y=stim_vector2, name="injected wave2"))
            fig_r.add_trace(go.Scatter(x=t, y=axon0_v_9,
                            name="axon(0_9)_v", line=dict(color="#3B1877")))
            fig_r.add_trace(go.Scatter(x=t, y=axon5_v_9,
                            name="axon(5_8)_v", line=dict(color="#DA5A2A")))
            fig_r.update_layout(
                width=800,
                yaxis_title="membrane potential (mV)",
                xaxis_title="Time (ns)",
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

        TI_result(location, delay, duration, dt, end_time, stim_t, plus_wave, impulse)