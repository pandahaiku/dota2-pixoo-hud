# Dota 2 HUD & GSI Integration Project

This project integrates Dota 2's GameState Integration (GSI) data with a custom heads-up display (HUD) rendered on a Pixoo display. It fetches hero and item images from the Dota 2 CDN, caches them for improved performance, and dynamically overlays game statistics (health, mana, K/D/A, level, gold, etc.) onto a HUD layout.

## Features

- **Custom GSI Configuration**: Automatically generate a configuration file for Dota 2's GSI.
- **Real-time Data Handling**: A Flask server receives GSI updates and publishes them via ZeroMQ.
- **Image Caching & Retrieval**: Downloads and caches hero portraits and item icons from the Dota 2 CDN.
- **Dynamic HUD Rendering**: Displays hero portrait, health/mana bars, K/D/A numbers, level, and inventory items.
- **Pixoo Integration**: Subscribes to ZeroMQ updates and pushes the generated HUD images to a Pixoo 64 display.

## Project Structure

```
├── config.py                      # Project configuration for GSI, ZeroMQ, Pixoo, etc.
├── create_dota_2_gsi_config.py    # Script to generate the Dota 2 GSI config file.
├── dota_2_cdn.py                  # Functions for fetching and caching images from Dota 2 CDN.
├── hud_renderer.py                # HUDRenderer class (HUD creation and caching).
├── gsi_pub.py                     # Flask server that receives GSI updates and publishes via ZeroMQ.
├── pixoo_sub.py                   # Subscriber that renders the HUD and pushes updates to the Pixoo display.
├── assets/                        # Contains assets (e.g., gold icon image).
└── cache/                         # Directories for cached hero and item images.
```

## Installation

### Prerequisites

- **Python 3.8+**: It is recommended to use Python 3.8 or later.
### Install Dependencies
Install the required packages using `requirements.txt`

```bash
pip install -r requirements.txt
```

## Configuration

Configuration settings are defined in `config.py`. Key settings include:

- **GSI Receiver**: IP and port settings for receiving data from Dota 2.
- **Flask Settings**: Host and port for the GSI server.
- **ZeroMQ Settings**: Addresses and ports for publishing/subscribing GSI data.
- **Pixoo Display**: IP address of your Pixoo display.
- **Steam GSI Config Directory**: Location where the custom GSI config will be created.
- **CDN URLs**: Templates for fetching hero and item images from the Dota 2 CDN.
- **Caching Directories**: Directories to store downloaded images.

Adjust these values in `config.py` to fit your system and network.

## Generating the GSI Configuration File

To create a custom Dota 2 GSI config file, run:

```bash
python create_dota_2_gsi_config.py
```

This will write a config file (e.g., `gamestate_integration_custom.cfg`) to the specified directory in your Steam installation.

## Running the Application

### Starting the GSI Publisher

Run the GSI publisher to start the Flask server which listens for game updates from Dota 2:

```bash
python gsi_pub.py
```

The server will listen on the host and port configured in `config.py` and publish JSON updates via ZeroMQ.

### Starting the Pixoo Subscriber

Run the Pixoo subscriber to listen for ZeroMQ updates, render the HUD, and push the image to your Pixoo display:

```bash
python pixoo_sub.py
```

This script instantiates the `HUDRenderer` class (from `hud_renderer.py`) to create a dynamic HUD based on incoming game state data.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions, bug reports, and feature requests are welcome. Please open an issue or submit a pull request on GitHub.

---

