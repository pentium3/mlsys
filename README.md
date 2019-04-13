# Project for csci8980 ML in Computer System

## Introduction

#### server: agent on Host side

Control the VPS and recommend new configuration for VPS.

#### client: agent on VPS side

Run benchmark and monitor performance metrics. Send the performance data to Host.

## Installation

1. Install python packages

```pip install -r requirements.txt```

2. Add ```python main.py``` to startup script in VPS

## Usage

Run ```python main.py``` on host side. Then the VPS will be automatically started.
