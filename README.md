# Forensic Reconstruction of Road Collisions from Independent Onboard Recordings

Code, dataset and article accompanying the paper by L. Bacchiani, A. Bedei, M. Bravetti, R. Girau and G. Pau (University of Bologna).

This project reconstructs road traffic collisions from independent onboard vehicle recordings. By combining radar observations, vehicle motion, positioning data and collision reports, the system reconstructs a shared chronology of the incident, including vehicle trajectories, collisions and events preceding the impact.

- **Article:** [paper/main.pdf](paper/main.pdf) (LaTeX source in [paper/](paper/)).
- **Dataset:** Recorded CARLA scenarios available in [traces/](traces/).

## Installation

**Requirements:**
- Windows 10/11
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- [CARLA 0.9.15](https://github.com/carla-simulator/carla/releases/tag/0.9.15) (Windows packaged build)
- GPU for graphical visualization

Clone the repository and create the Conda environment:

```bat
git clone https://github.com/AndreaBedei1/Cooperative_Forensic_Replay.git
cd Cooperative_Forensic_Replay
conda env create -f environment.yml
conda activate carla
```

Configure the CARLA installation path:

```bat
set CARLA_ROOT=C:\path\to\CARLA_0.9.15\WindowsNoEditor
```

Replace the path with your actual CARLA installation directory. Set `CARLA_ROOT` again when opening a new terminal.

All commands below must be executed from the repository root with the `carla` environment activated.

## Viewing Replays

Recorded scenarios are stored in `traces/`. Each run can be visualized using two viewers:

- **Reconstruction:** Displays the reconstructed vehicle trajectories, radar tracks, collisions and events.
- **Ground Truth:** Displays the original simulation data for comparison.

### 1. Start CARLA

Open a terminal and start the CARLA server:

```bat
python scripts\start_carla.py --carla-root %CARLA_ROOT% --port 3000
```

### 2. View a Reconstruction

In another terminal, run:

```bat
python scripts\replay_run.py traces\S12\run_0_crash --port 3000
```

Replace `traces\S12\run_0_crash` with the path of any other recorded run.

### 3. Compare Reconstruction and Ground Truth

To visualize both views side by side, start a second CARLA server in a separate terminal:

```bat
python scripts\start_carla.py --carla-root %CARLA_ROOT% --port 3100
```

Then launch the two viewers in separate terminals:

**Ground Truth:**
```bat
python scripts\view_ground_truth.py traces\S12\run_0_crash --port 3100 --sync-lead 47811 --res 960x540
```

**Reconstruction:**
```bat
python scripts\replay_run.py traces\S12\run_0_crash --port 3000 --sync-follow 47811 --res 960x540
```

Both viewers are synchronized for playback and navigation.

### Playback Controls

| Key | Action |
|---|---|
| `SPACE` | Play / Pause |
| `LEFT / RIGHT` | Move backward / forward |
| `1–4` | Change playback speed |
| `N / P` | Next / previous event |
| `C` | Change camera |
| `TAB` | Select vehicle |
| `T` | Show / hide radar tracks |
| `ESC` | Exit viewer |

### Export Replay Images

Top-down replay images can also be generated without starting a CARLA server:

```bat
python scripts\replay_run.py traces\S12\run_0_crash --export out\s12 --at -1 --at 0 --format png
```

## Collecting New Data

Scenarios are defined in `configs/scenarios/` (S01–S19, with their variants). With CARLA running, acquire one run with:

```bat
python scripts\run_scenario.py --scenario S01 --variant crash --output scratch\traces
```

The script connects to CARLA on port 3000 (and starts it if no server is running). The run is written to `<output>\<scenario>\run_<seed>_<variant>`. **Always pass `--output`:** the default is `traces`, so with the default seed 0 the recorded campaign runs would be overwritten. Then reconstruct and evaluate the new run:

```bat
python scripts\reconstruct_run.py scratch\traces\S01\run_0_crash --evaluate
```

## Reproducing the Perturbation Campaigns

The scripts below read the recorded runs and write perturbed copies elsewhere; `traces/` is never modified. Point `--work` and `--results` to `scratch\` to keep the committed results in `results/` unchanged.

**Sensor and positioning perturbations** (radar, GNSS and combined families of the paper, all 22 runs):

```bat
python scripts\robustness.py --scenarios --families baseline,gnss,radar_v3,radar_asym,radar_gnss_v3,radar_asym_gnss --work scratch\robustness --results scratch\robustness_results
```

**Clock residuals and crash-recorder reports** (needs `CARLA_ROOT` for the OpenDRIVE maps, or `--maps <folder of .xodr>`):

```bat
python scripts\clock_edr_study.py --work scratch\clock_edr --results scratch\clock_edr_results
```

**Paper tables** from the committed results in `results/`:

```bat
python scripts\paper_reconstruction_metrics.py --out scratch\paper\reconstruction_metrics.json
python scripts\paper_event_metrics.py --out scratch\paper
python scripts\paper_geometry_comparison.py --out-dir scratch\paper
```

Interrupted campaigns resume from the `jobs.jsonl` in the results folder.

## License

MIT License. See [LICENSE](LICENSE).