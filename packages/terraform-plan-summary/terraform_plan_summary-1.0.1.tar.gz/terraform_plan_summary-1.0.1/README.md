# terraform-plan-summary

A Python command-line tool that transforms Terraform plan outputs into clean, hierarchical tree views with color-coded changes. Easily visualize your infrastructure changes organized by modules with detailed attribute-level inspection.

## Installation

### From PyPI

Using uv:

```bash
uv pip install terraform-plan-summary
```

Or run directly with uvx:

```bash
uvx terraform-plan-summary
```

## Requirements

- Python 3.13 or higher
- Terraform CLI (for processing binary plan files)

## Usage

### Basic Usage

```bash
# From a JSON plan file
terraform-plan-summary plan.json

# From a binary plan file (requires terraform CLI)
terraform-plan-summary plan.out
```

### Command Line Options

```bash
terraform-plan-summary [OPTIONS] PLAN_FILE

Arguments:
  PLAN_FILE                 Path to Terraform plan file (binary .out or JSON)

Options:
  -v, --verbose             Show changed attributes (-v) or their values (-vv)
  --show-ids                Display resource identifiers (name, ARN, ID, etc.)
  -h, --help               Show help message
```

### Examples

#### Basic Tree View
```bash
terraform-plan-summary plan.json
```
```
root_module
├── + aws_instance.web_server
├── ~ aws_security_group.web_sg
└── database
    ├── + aws_db_instance.main
    └── - aws_db_subnet_group.legacy
```

#### With Resource Identifiers
```bash
terraform-plan-summary --show-ids plan.json
```
```
root_module
├── + aws_instance.web_server (web-server-prod)
├── ~ aws_security_group.web_sg (sg-0abc123def456789)
└── database
    ├── + aws_db_instance.main (prod-database)
    └── - aws_db_subnet_group.legacy (legacy-subnet-group)
```

#### Detailed Attribute Changes
```bash
terraform-plan-summary -vv --show-ids plan.json
```
```
root_module
├── + aws_instance.web_server (web-server-prod)
├── ~ aws_security_group.web_sg (sg-0abc123def456789)
│   ├── ~ ingress: [] -> [{"cidr_blocks":["0.0.0.0/0"],"from_port":80,"protocol":"tcp","to_port":80}]
│   └── + name: "web-security-group"
└── database
    ├── + aws_db_instance.main (prod-database)
    └── - aws_db_subnet_group.legacy (legacy-subnet-group)
        └── - subnet_ids: ["subnet-abc123","subnet-def456"]
```

## Generating Terraform Plans

### JSON Format (Recommended)
```bash
terraform plan -out=plan.out
terraform show -json plan.out > plan.json
terraform-plan-summary plan.json
```

### Binary Format
```bash
terraform plan -out=plan.out
terraform-plan-summary plan.out
```
