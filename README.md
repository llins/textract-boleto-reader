# textract-boleto-reader

This project aims to show the art of the possible in relation to the use of [Amazon Textract](https://aws.amazon.com/textract/) to read and extract all fields and values from Brazilian bank slips (Boleto), as well as the barcode number.

> **The code within this repository comes with no guarantee, the use of this code is your responsibility. I take NO responsibility and/or liability for how you choose to use any of the source code available here. By using any of the files available in this repository, you understand that you are AGREEING TO USE AT YOUR OWN RISK. Once again, ALL files available here are for EDUCATION and/or RESEARCH purposes ONLY.**

## Architecture

<p align="center">
  <img src="/doc/arch.png">
</p>

**Sample result (BoletoAnalysisResultTopic message)**

```json
{
  "DocumentLocation": {
    "S3ObjectName": "BOLETO_19541490_066369169.PDF",
    "S3Bucket": "textract-boleto-reader-boletobucket-999999999999"
  },
  "KeyValuePairs": {
    "Espécie Doc. ": "RC ",
    "Agência / Código do Beneficiário ": "8541/41906-8 ",
    "Espécie Moeda ": "R$ ",
    "Uso do Banco ": "",
    "Data de Vencimento ": "10/01/2021",
    "Data do Documento ": "10/01/2021",
    "N° do Documento ": "19541490 ",
    "Carteira ": "109 ",
    "Aceite ": "N ",
    "Nosso Número ": "109/06636916-9 ",
    "Data de Processamento ": "09/01/2021",
    "CNPJ/CPF ": "74.879.565/4789-45 ",
    "Quantidade Moeda ": "",
    "Valor Moeda ": "",
    "(=) Valor Cobrado ": "",
    "Nome do Beneficiário ": "Loja XYZ S/A - SAO PAULO - SP ",
    "Nosso Número / Cód. do Documento ": "109/06636916-9 ",
    "Valor Cobrado ": "597,66 ",
    "Vencimento ": "10/01/2021",
    "(+) Outros Acréscimos ": "0,00 ",
    "Local de Pagamento ": "VÁLIDO ATÉ O VENCIMENTO, PAGUE PREFERENCIALMENTE NO BANCO X",
    "(=) Valor do Documento ": "597,66 ",
    "(-) Desconto/ Abatimento ": "0,00 ",
    "PARCELA : ": "0506 ",
    "Beneficiário ": "Loja XYZ S/A - SAO PAULO - SP ",
    "(+) Mora Multa ": "0,00 ",
    "(-) Outras Deduções ": "0,00 ",
    "Pagador ": "BRUCE WAYNE 555.444.333-22 ",
    "Autenticação Mecânica ": "",
    "BarcodeNumber": "34191090656369169854014190680000684350000059766"
  }
}
```


## File Structure

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes [Lambda Powertools for operational best practices](https://github.com/awslabs/aws-lambda-powertools-python), and the following files and folders.

- **`src`** - Code for the application's Lambda function.
- **`events`** - Invocation events that you can use to invoke the function.
- **`tests`** - Unit tests for the application code. 
- **`template.yaml`** - A template that defines the application's AWS resources.
- **`Makefile`** - Makefile for your convenience to install deps, build, invoke, and deploy your application.

## Requirements

**Make sure you have the following installed before you proceed**

* AWS CLI - [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) configured with Administrator permission
* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

## Deploy the sample application

> **Already know this sample? Run: `make hurry` - This command will install app deps, build, and deploy your Serverless application using SAM.**

Build and deploy your application for the first time by running the following commands in your shell:

```bash
textract-boleto-reader$ make build
textract-boleto-reader$ make deploy.guided
```

The first command will **build** the source of your application within a Docker container. The second command will **package and deploy** your application to AWS. Guided deploy means SAM CLI will ask you about the name of your deployment/stack, AWS Region, and whether you want to save your choices, so that you can use `make deploy` next time.

## Unit tests

Tests are defined in the `tests` folder in this project, and we use Pytest as the test runner for this sample project.

Make sure you install dev dependencies before you run tests with `make dev`:

```bash
textract-boleto-reader$ make dev
textract-boleto-reader$ make test
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
textract-boleto-reader$ aws cloudformation delete-stack --stack-name textract-boleto-reader
```

# Appendix

## Powertools

**Tracing**

[Tracer utility](https://awslabs.github.io/aws-lambda-powertools-python/core/tracer/) patches known libraries, and trace the execution of this sample code including the response and exceptions as tracing metadata - You can visualize them in AWS X-Ray.

**Logger**

[Logger utility](https://awslabs.github.io/aws-lambda-powertools-python/core/logger/) creates an opinionated application Logger with structured logging as the output, dynamically samples 10% of your logs in DEBUG mode for concurrent invocations, log incoming events as your function is invoked, and injects key information from Lambda context object into your Logger - You can visualize them in Amazon CloudWatch Logs.

**Metrics**

[Metrics utility](https://awslabs.github.io/aws-lambda-powertools-python/core/metrics/) captures cold start metric of your Lambda invocation, and could add additional metrics to help you understand your application KPIs - You can visualize them in Amazon CloudWatch.

## Sync project with function dependencies

Pipenv takes care of isolating dev dependencies and app dependencies. As SAM CLI requires a `requirements.txt` file, you'd need to generate one if new app dependencies have been added:

```bash
textract-boleto-reader$ pipenv lock -r > src/requirements.txt
```
