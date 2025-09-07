# ModelAudit

Static security scanner for AI/ML model files. It detects malicious code, dangerous deserialization, risky module usage, and embedded secrets—all without loading or executing the model.

[![PyPI version](https://badge.fury.io/py/modelaudit.svg)](https://pypi.org/project/modelaudit/)
[![Python versions](https://img.shields.io/pypi/pyversions/modelaudit.svg)](https://pypi.org/project/modelaudit/)
[![Code Style: ruff](https://img.shields.io/badge/code%20style-ruff-005cd7.svg)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/github/license/promptfoo/promptfoo)](https://github.com/promptfoo/promptfoo/blob/main/LICENSE)

<img width="989" alt="image" src="https://www.promptfoo.dev/img/docs/modelaudit/modelaudit-result.png" />

**[Documentation](https://www.promptfoo.dev/docs/model-audit/)** | **[Usage Examples](https://www.promptfoo.dev/docs/model-audit/usage/)** | **[Supported Formats](https://www.promptfoo.dev/docs/model-audit/scanners/)**

## Quick Start

```bash
# Install with all supported ML framework dependencies
pip install modelaudit[all]

# Scan a model file
modelaudit model.pkl

# Scan a directory
modelaudit ./models/

# Export results for automation
modelaudit model.pkl --format json --output results.json
```

**Example output:**

```text
$ modelaudit suspicious_model.pkl

✓ Scanning suspicious_model.pkl
Files scanned: 1 | Issues found: 2 critical, 1 warning

1. suspicious_model.pkl (pos 28): [CRITICAL] Malicious code execution attempt
   Why: Contains os.system() call that could run arbitrary commands

2. suspicious_model.pkl (pos 52): [WARNING] Dangerous pickle deserialization
   Why: Could execute code when the model loads

✗ 2 security issues found. See details above.
```

## Installation

**Recommended (includes common ML frameworks):**

```bash
pip install modelaudit[all]
```

**Basic installation:**

```bash
# Core functionality only (pickle, numpy, archives)
pip install modelaudit
```

**Specific frameworks:**

```bash
pip install modelaudit[tensorflow]  # TensorFlow (.pb)
pip install modelaudit[pytorch]     # PyTorch (.pt, .pth)
pip install modelaudit[h5]          # Keras (.h5, .keras)
pip install modelaudit[onnx]        # ONNX (.onnx)
pip install modelaudit[safetensors] # SafeTensors (.safetensors)

# Multiple frameworks
pip install modelaudit[tensorflow,pytorch,h5]
```

**Additional features:**

```bash
pip install modelaudit[cloud]       # S3, GCS, Azure storage
pip install modelaudit[coreml]      # Apple Core ML
pip install modelaudit[flax]        # JAX/Flax models
pip install modelaudit[mlflow]      # MLflow registry
pip install modelaudit[huggingface] # Hugging Face integration
```

**Compatibility:**

```bash
# NumPy 1.x compatibility (some frameworks require NumPy < 2.0)
pip install modelaudit[numpy1]

# For CI/CD environments (omits dependencies like TensorRT that may not be available)
pip install modelaudit[all-ci]
```

**Docker:**

```bash
docker pull ghcr.io/promptfoo/modelaudit:latest
# Linux/macOS
docker run --rm -v "$(pwd)":/app ghcr.io/promptfoo/modelaudit:latest model.pkl
# Windows
docker run --rm -v "%cd%":/app ghcr.io/promptfoo/modelaudit:latest model.pkl
```

## Security Checks

### Code Execution Detection

- Dangerous Python modules: `os`, `sys`, `subprocess`, `eval`, `exec`
- Pickle opcodes: `REDUCE`, `GLOBAL`, `INST`, `OBJ`, `NEWOBJ`, `STACK_GLOBAL`, `BUILD`, `NEWOBJ_EX`
- Embedded executable file detection

### Embedded Data Extraction

- API keys, tokens, and credentials in model weights/metadata
- URLs, IP addresses, and network endpoints
- Suspicious configuration properties

### Archive Security

- Path traversal attacks in ZIP/TAR archives
- Executable files within model packages
- Malicious filenames and directory structures

### ML Framework Analysis

- TensorFlow operations: `PyFunc`, `PyFuncStateless`
- Keras unsafe layers and custom objects
- Template injection in model configurations

### Context-Aware Analysis

- Intelligently distinguishes between legitimate ML framework patterns and genuine threats to reduce false positives in complex model files

## Supported Formats

ModelAudit includes 29 specialized scanners for ML model formats ([see complete list](https://www.promptfoo.dev/docs/model-audit/scanners/)):

| Format          | Extensions                                | Security Focus                                     |
| --------------- | ----------------------------------------- | -------------------------------------------------- |
| **Pickle**      | `.pkl`, `.pickle`, `.dill`, `.pt`, `.pth` | Code execution, malicious opcodes, deserialization |
| **Archives**    | `.zip`, `.tar`, `.gz`, `.7z`, `.bz2`      | Path traversal, embedded executables               |
| **TensorFlow**  | `.pb`, SavedModel directories             | Dangerous operations, custom ops                   |
| **Keras**       | `.h5`, `.keras`, `.hdf5`                  | Unsafe layers, custom objects                      |
| **ONNX**        | `.onnx`                                   | Custom operators, metadata                         |
| **SafeTensors** | `.safetensors`                            | Header validation, metadata                        |
| **GGUF/GGML**   | `.gguf`, `.ggml`                          | Header validation, metadata                        |
| **Joblib**      | `.joblib`                                 | Pickled objects, scikit-learn                      |
| **JAX/Flax**    | `.msgpack`, `.flax`, `.orbax`             | Serialized transforms                              |
| **NumPy**       | `.npy`, `.npz`                            | Array metadata, pickle objects                     |
| **Core ML**     | `.mlmodel`                                | Custom layers, metadata                            |
| **ExecuTorch**  | `.ptl`, `.pte`                            | Mobile model validation                            |

Plus scanners for TensorFlow Lite, TensorRT, PaddlePaddle, OpenVINO, text files, and configuration formats.

[Complete format documentation →](https://www.promptfoo.dev/docs/model-audit/scanners/)

## Usage Examples

### Basic Scanning

```bash
# Scan single file
modelaudit model.pkl

# Scan directory
modelaudit ./models/

# Strict mode (fail on warnings)
modelaudit model.pkl --strict
```

### CI/CD Integration

```bash
# JSON output for automation
modelaudit models/ --format json --output results.json

# Generate SBOM report
modelaudit model.pkl --sbom compliance_report.json

# Disable colors in CI
NO_COLOR=1 modelaudit models/
```

### Remote Sources

```bash
# Hugging Face models (via direct URL or hf:// scheme)
modelaudit https://huggingface.co/gpt2
modelaudit hf://microsoft/DialoGPT-medium

# Cloud storage
modelaudit s3://bucket/model.pt
modelaudit gs://bucket/models/
modelaudit https://account.blob.core.windows.net/container/model.pt

# MLflow registry
modelaudit models:/MyModel/Production

# JFrog Artifactory
modelaudit https://company.jfrog.io/repo/model.pt
```

### Command Options

- **`--format`** - Output format: text, json, sarif
- **`--output`** - Write results to file
- **`--verbose`** - Detailed output
- **`--quiet`** - Minimal output
- **`--strict`** - Fail on warnings, scan all files
- **`--timeout`** - Override scan timeout
- **`--max-size`** - Set size limits (e.g., 10 GB)
- **`--dry-run`** - Preview without scanning
- **`--progress`** - Force progress display
- **`--sbom`** - Generate CycloneDX SBOM
- **`--blacklist`** - Additional patterns to flag
- **`--no-cache`** - Disable result caching

[Advanced usage examples →](https://www.promptfoo.dev/docs/model-audit/usage/)

## Output Formats

### Text (default)

```text
$ modelaudit model.pkl

✓ Scanning model.pkl
Files scanned: 1 | Issues found: 1 critical

1. model.pkl (pos 28): [CRITICAL] Malicious code execution attempt
   Why: Contains os.system() call that could run arbitrary commands
```

### JSON (for automation)

```bash
modelaudit model.pkl --format json
```

```json
{
  "files_scanned": 1,
  "issues": [
    {
      "message": "Malicious code execution attempt",
      "severity": "critical",
      "location": "model.pkl (pos 28)"
    }
  ]
}
```

### SARIF (for security tools)

```bash
modelaudit model.pkl --format sarif --output results.sarif
```

## Troubleshooting

### Check scanner availability

```bash
modelaudit doctor --show-failed
```

### NumPy compatibility issues

```bash
# Use NumPy 1.x compatibility mode
pip install modelaudit[numpy1]
```

### Missing dependencies

```bash
# ModelAudit shows exactly what to install
modelaudit your-model.onnx
# Output: "Install with 'pip install modelaudit[onnx]'"
```

### Exit Codes

- `0` - No security issues found
- `1` - Security issues detected
- `2` - Scan errors occurred

### Authentication

ModelAudit uses environment variables for authenticating to remote services:

```bash
# JFrog Artifactory
export JFROG_API_TOKEN=your_token

# MLflow
export MLFLOW_TRACKING_URI=http://localhost:5000

# AWS, Google Cloud, and Azure
# Authentication is handled automatically by the respective client libraries
# (e.g., via IAM roles, `aws configure`, `gcloud auth login`, or environment variables).
# For specific env var setup, refer to the library's documentation.
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Hugging Face
export HF_TOKEN=your_token
```

## Documentation

- **Documentation**: [promptfoo.dev/docs/model-audit/](https://www.promptfoo.dev/docs/model-audit/)
- **Usage Examples**: [promptfoo.dev/docs/model-audit/usage/](https://www.promptfoo.dev/docs/model-audit/usage/)
- **Report Issues**: Contact support at [promptfoo.dev](https://www.promptfoo.dev/)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
