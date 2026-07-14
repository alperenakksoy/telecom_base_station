# Telecom Base Station Load Simulation

**Author:** Ahmet Alperen Aksoy = 38421

A mathematical model and interactive simulation visualizing how base stations in a city telecom network experience traffic load and overloading over a typical 24-hour period.

---

## 📖 Overview

Telecom companies manage hundreds of base stations spread across cities. Throughout the day, these stations go through predictable stress cycles: quiet at night, heavily loaded during the morning commute, and critically stressed during the evening rush.

Testing capacity limits on a live network risks outages and dropped calls. This project solves that problem by building a mathematical model of **400 base stations (a 20×20 grid)** and simulating their traffic load using **ordinary differential equations (ODEs)**. The result is an interactive animated heatmap where you can observe load dynamics and tweak network parameters in real time.

---

## 🚀 How to Run

Launch the simulation with the live animated heatmap and interactive controls:

```bash
python main.py --interactive
```

---

## 🏗️ Project Architecture

The project follows the simulation architecture proposed by **Durán (2020)**, separating the implementation into three distinct layers.

### Mathematical Model (`Mᵢ`)

**`models/load_model.py`**

Contains the mathematical equations that describe the telecom network. This module defines the model only—no numerical computation or solving happens here.

### Kernel Solver (`KSᵢ`)

**`kernel/solver.py`**

Executes the mathematical model using `scipy.integrate.odeint`.

For the default configuration:

- 400 base stations
- 240 simulation time steps
- **96,000 ODE evaluations**

This layer converts the mathematical equations into numerical solutions.

### Integration Layer (`IMₖ`)

**`integration/animator.py`**
**`integration/interactive.py`**

Responsible for visualization and user interaction.

These modules:

- render the animated heatmap,
- update station colors over time,
- provide interactive sliders for changing simulation parameters.

---

# 🧮 Mathematics & Core Logic

The simulation is built around three mathematical components executed in sequence.

## 1. City Weight Map (Geography)

Each base station receives a geographic weight depending on its distance from the city center.

The model uses exponential decay:

\[
weight = 0.4 + 1.1 \times e^{-r \times dist}
\]

where:

- **dist** = distance from the city center
- **r** = geographic decay constant

This reflects real cities:

- downtown stations serve many users,
- suburban stations serve fewer users.

Consequently, the center station attracts nearly three times more traffic than stations in the corners.

---

## 2. Traffic Demand (Time-Varying Load)

The incoming traffic at time *t* is modeled as:

\[
\lambda(t)
=
amp
\times
e^{-\lambda |t-t_{peak}|}
\times
weight
\]

Traffic rises smoothly toward each peak and then gradually decreases.

### WEEKDAY_PROFILE

The weekday behavior is defined by:

```python
(8, 0.6, 0.5, 18, 0.9, 0.4, 0.1)
```

Each value has a specific meaning.

| Value | Meaning |
|--------|---------|
| **8** | Morning peak occurs at **08:00** |
| **0.6** | Morning peak amplitude |
| **0.5** | Morning decay rate |
| **18** | Evening peak occurs at **18:00** |
| **0.9** | Evening peak amplitude |
| **0.4** | Evening decay rate |
| **0.1** | Night-time baseline traffic |

### Morning Peak

The morning rush is centered around **08:00**, representing people commuting to work.

The amplitude (**0.6**) is moderate because commuters leave home over a relatively wide time window.

The decay rate (**0.5**) causes traffic to fall relatively quickly once the commute ends.

### Evening Peak

The evening rush begins around **18:00**.

Its amplitude (**0.9**) is larger because a much larger fraction of the population leaves work during roughly the same period.

The decay rate (**0.4**) is smaller, causing traffic to remain elevated for longer than the morning rush.

### Night Baseline

Traffic never reaches zero.

Even at **03:00**, devices continue to:

- synchronize cloud data,
- receive notifications,
- perform operating-system updates,
- maintain messaging connections.

The baseline value (**0.1**) models this constant background activity.

---

## 3. Load Dynamics (Main ODE)

The network load evolves according to:

\[
\frac{dL}{dt}
=
\lambda(t)
-
\mu L
\]

where:

- **λ(t)** = incoming traffic demand
- **μ** = maximum processing capacity of the base station
- **L** = current normalized load

Typical interpretations are:

- **L = 0.0** → idle
- **L = 1.0** → fully utilized
- **L > 1.0** → overloaded

---

### Why Multiply μ by L?

A base station cannot process traffic that does not exist.

If the station is only **20% loaded**, only about **20% of its processing capacity** is actually being used.

Therefore, the processing rate should scale with the current load:

\[
processing = \mu L
\]

instead of simply using

\[
processing = \mu
\]

This produces several realistic properties.

#### 1. Self-Regulating Behavior

When the station becomes heavily loaded, the processing rate automatically increases.

When traffic decreases, the processing rate naturally becomes smaller.

This creates a stable feedback system.

#### 2. Prevents Negative Loads

During quiet nighttime hours, incoming traffic is extremely small.

If a constant processing rate were used, the mathematical model could remove more traffic than actually exists, producing impossible negative loads.

Multiplying by **L** causes the drain rate to approach zero as the station empties, preventing this problem automatically.

#### 3. Matches Real Networks

Real telecommunications equipment processes only active traffic.

An idle base station consumes energy but does not continuously process nonexistent packets.

The term **μL** therefore reflects realistic network behavior.

---

# 🎛️ Interactive Controls

Running the interactive simulation provides sliders for modifying the network environment in real time.

## μ (Network Capacity)

Represents the processing capability of each base station.

- Lower values simulate weaker infrastructure.
- Stations overload more quickly.
- More cells become red.

Increasing μ allows stations to process traffic faster, keeping the network stable.

---

## City Density

Scales the geographic weight map.

Higher density means:

- more users near the city center,
- heavier downtown congestion,
- suburban stations remain comparatively light.

---

## Day of the Week

Changes the traffic profile.

For example:

- weekday morning peak → **08:00**
- Saturday morning peak → **11:00**

Similarly, the evening peak shifts later because shopping and leisure activities replace work commuting.

Overall traffic is also reduced due to the absence of office commuters.

---

# 📂 Repository Structure

```text
telecom_base_station/
├── main.py                     # Entry point
├── network_load_sim/
│   ├── models/
│   │   └── load_model.py       # Mathematical equations (Mᵢ)
│   ├── kernel/
│   │   └── solver.py           # Numerical ODE solver (KSᵢ)
│   ├── integration/
│   │   ├── animator.py         # Animated heatmap (IMₖ)
│   │   └── interactive.py      # Interactive controls (IMₖ)
│   ├── tests/
│   │   └── test_model.py       # Unit tests
│   └── requirements.txt        # Python dependencies
```

> **Note:** The directory structure shown above is inferred from the project organization.