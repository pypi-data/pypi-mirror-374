<p align="center">
    <a href="https://github.com/tanaos/synthex">
        <img src="https://raw.githubusercontent.com/tanaos/synthex/master/assets/banner.png" width="600px" alt="Synthex - Generate high quality, synthetic datasets">
    </a>
</p>

<p align="center">
    <a href="https://tanaos.com">Learn more</a>
    ·
    <a href="https://docs.tanaos.com/synthex/intro">Documentation</a>
    ·
    <a href="https://colab.research.google.com/github/tanaos/tanaos-docs/blob/master/blueprints/synthex/housing_market_analysis_dataset.ipynb">Demo</a>
</p>

<p align="center">
    <a href="https://pypi.org/project/synthex/">
        <img src="https://img.shields.io/pypi/v/synthex?logo=pypi&logoColor=%23fff&color=%23006dad&label=Pypi"
        alt="Latest PyPi package version">
    </a>
    <a href="https://github.com/tanaos/synthex/actions/workflows/python-publish.yml">
        <img src="https://img.shields.io/github/actions/workflow/status/tanaos/synthex/python-publish.yml?logo=github&logoColor=%23fff&label=Tests"
        alt="Tests status">
    </a>
    <a href="https://huggingface.co/datasets?sort=trending&search=tanaos">
        <img src="https://img.shields.io/badge/Datasets-Sample_on_HuggingFace-red?logo=huggingface&logoColor=white&labelColor=grey"
            alt="Sample Datasets on HuggingFace">
    </a>
    <a href="https://github.com/tanaos/synthex/commits/">
        <img src="https://img.shields.io/github/commit-activity/m/tanaos/synthex?logo=git&logoColor=white&style=flat&color=purple&label=Commit%20Activity" alt="GitHub commit activity">
    </a>
    <a href="https://docs.tanaos.com/synthex/intro">
        <img src="https://img.shields.io/badge/Docs-Read_the_docs-orange?logo=docusaurus&logoColor=white"
            alt="Synthex Documentation">
    </a>
</p>

<p align="center">
    <strong>🚀 Generate any structured dataset from scratch • 👤 Anonymize your dataset and be GDPR-compliant</strong>
</p>

## 🔥 Highlights

- **Want to train a AI model, but don't have a training dataset?** Describe it to Synthex and it will generate it for you.
- **Need to anonymize your dataset to be GDPR-compliant?** Synthex can replicate your dataset and remove Personally Identifiable Information (PII).
- **Need to test your software, but don't yet have customer data?** Synthex will generate a dataset for you.

## ⏩ Demo

Don't have time to go through this README? We got you covered. Just click on the button below for an **interactive demo**.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tanaos/tanaos-docs/blob/master/blueprints/synthex/housing_market_analysis_dataset.ipynb)

## Introduction

Synthex is a Python library for generating large-scale, high-quality synthetic datasets. It is helpful in cases in which *real* data is too **limited**, **unbalanced**, completely **absent** or **contains Personal Identifiable Information (PII)**.

### Features & Use Cases

#### Key Features

- **Generate any dataset from scratch**: you don't need any data at all; Synthex will generate any structured dataset, even if it has no sample dataset to copy from.
- **Natural language description**: describe your requirements and any constraint the dataset may have in natural language.
- **Specify fields and types**: Synthex allows you to specify your dataset schema, including field names and types.

#### Use Cases:

- **AI Model Training**: lacking training data is no longer an issue; generate any training dataset for AI models with Synthex.
- **Dataset anonymization**: need a dataset without Personally Identifiable Information to be GDPR-compliant? Synthex is anonymous by default.
- **Software testing**: we all know testing your new software without customer data is not easy. Synthex will generate a testing dataset for you, so you can populate your DB.

## 🚀 Quickstart Guide

### Installation

Install the library with

```python
pip install synthex
```

### Basic Usage

To create a new dataset, use `Synthex.jobs.generate_data()`. For this method's full documentation, [see the Tanaos Docs](https://docs.tanaos.com/synthex/jobs/generate-data).

```python
from synthex import Synthex

client = Synthex()

client.jobs.generate_data(
    schema_definition = {
        "surface": {"type": "float"},
        "number_of_rooms": {"type": "integer"},
        "construction_year": {"type": "integer"},
        "city": {"type": "string"},
        "market_price": {"type": "float"}
    },
    examples = [
        {
            "surface": 104.00,
            "number_of_rooms": 3,
            "construction_year": 1985,
            "city": "Nashville",
            "market_price": 218000.00
        },
        {
            "surface": 98.00,
            "number_of_rooms": 2,
            "construction_year": 1999,
            "city": "Springfield",
            "market_price": 177000.00
        },
        {
            "surface": 52.00,
            "number_of_rooms": 1,
            "construction_year": 2014,
            "city": "Denver",
            "market_price": 230000.00
        }
    ],
    requirements = [
        "The 'market price' field should be realistic and should depend on the characteristics of the property.",
        "The 'city' field should specify cities in the USA, and the USA only"
    ],
    output_path = "output_data/output.csv",
    number_of_samples = 100,
    output_type = "csv"
)
```

where the parameters are as follows:

- `schema_definition`: A `dict` which specifies the output dataset's schema. It must have the following format:
    ```python
    {
        "<name_of_column_1>": {"type": "<datatype_of_column_1>"},
        "<name_of_column_2>": {"type": "<datatype_of_column_2>"},
        ...
        "<name_of_column_n>": {"type": "<datatype_of_column_n>"}
    }
    ```

    the possible values of `"type"` are `"string"`, `"integer"` and `"float"`.

- `examples`: A `List[dict]`, which specifies a few (3 to 5 are enough) sample datapoints that will help the data generation model understand what the output data should look like. They must have the same schema as the one specified in the `schema_definition` parameter, or an exception will be raised.

- `requirements`: a `List[str]`, where each string specifies a requirement or constraint for the job. It can be an empty list if no specific requirements are present.

- `output_path`: a `str` which specifies the path where the output dataset will be generated. It does not need to contain a file name, as this will be added automatically if one is not provided. If `output_path` does contain a file name, its extension must be consistent with the `output_type` parameter. If this is the case, the provided `output_path` is used in its entirety. Otherwise, the provided extension is replaced with one that is consistent with `output_type`. For example:

- `number_of_samples`: an `int` which specifies the number of datapoints that the model should generate. Keep in mind that the maximum number of datapoints you can generate with a single job depends on whether you are on a free or paid plan. For example:

- `output_type`: a `str` which specifies the format of the output dataset. Only `"csv"` (meaning a .csv file will be generated) is supported at this time, but we will soon add more options.

## 🔗 Sample Datasets & Demos

- **Demo - Create your first Synthetic Dataset**: an interactive tutorial on how to use Synthex to create your first synthetic dataset ([Live Demo](https://colab.research.google.com/github/tanaos/tanaos-docs/blob/master/blueprints/synthex/housing_market_analysis_dataset.ipynb))
- **Online Store Chatbot Guardrail Training Dataset:** a synthetic dataset, created with Synthex, used for training a Guardrail Model for an online store chatbot ([See Dataset on HuggingFace](https://huggingface.co/datasets/tanaos/online-store-chatbot-guardrail-training-dataset)).

## 🔑 Plans

**Free plan**: each user enjoys 1500 datapoints per month and 500 datapoints per job for free.

**Pay-as-you-go**: for additional usage beyond the free tier:
1. create an account on [our platform](https://platform.tanaos.com) 
2. add credits to it
3. create an Api Key and pass it to Synthex at initialization:
    ```python
    from synthex import Synthex

    client = Synthex(
        api_key="<your-api-key>"
    )
    ```
    The pay-as-you-go pricing is **1$ per 100 datapoints**. Once you finish your credits, if you have not exceeded the monthly limit, you will be **automatically switched to the free plan**.


## 📚 Documentation & Support

- Full documentation: https://docs.tanaos.com/synthex
- Contact: info@tanaos.com
