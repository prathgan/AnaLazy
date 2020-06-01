# AnaLazy

AnaLazy is a graphical web or desktop application which enables analysts to train a machine learning model off of a spreadsheet of training data and then make useful predictions, all without having to write a single line of code. AnaLazy also has a built-in data quality analysis tool to allow you to ensure your data is up to par before training a model with it.

## Installation

Download the code from the [GitHub repository](https://github.com/prathgan/AnaLazy) and install all dependencies by `cd`ing to AnaLazy's root directory and

```bash
pip install -r requirements.txt
```

Then create internal directories for backend use

```bash
mkdir uploads
mkdir models
```

## Usage
Navigate in a terminal to the root of the folder with the AnaLazy app code.

To run AnaLazy in the standard configuration (GUI will automatically open)
```bash
python index.py
```

Use the `--web` flag to open app in default browser instead of as a standalone GUI and the `--debug` flag to enable hot reloading and disable automatic page opening on restart.

## Images


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)