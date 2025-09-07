# Cinetica

Cinetica es una librería de Python diseñada para proporcionar varios módulos para cálculos y simulaciones de física, incluyendo movimientos rectilíneos, parabólicos, circulares, oscilatorios, relativos y espaciales (3D).

## Instalación

```bash
pip install cinetica
```

Para documentación detallada y ejemplos de uso, por favor consulta [DOCS.md](DOCS.md).

## Desarrollo

### Instalación para desarrollo

```bash
pip install -e ".[dev]"
```

### Herramientas de linting

Este proyecto utiliza las siguientes herramientas de linting para mantener la calidad del código:

- **Black**: Formateador de código automático
- **Flake8**: Linter para detectar errores de estilo y problemas de código
- **MyPy**: Verificador de tipos estáticos

#### Ejecutar todas las herramientas de linting

```bash
# Verificar sin modificar archivos
python lint.py

# Auto-corregir problemas de formato
python lint.py --fix
```

#### Ejecutar herramientas individualmente

```bash
# Black (formateador)
black cinetica/ tests/ usage/
black --check cinetica/ tests/ usage/  # solo verificar

# Flake8 (linter)
flake8 cinetica/ tests/ usage/

# MyPy (verificador de tipos)
mypy cinetica/
```

#### Pre-commit hooks (opcional)

Para ejecutar automáticamente las herramientas de linting antes de cada commit:

```bash
# Instalar pre-commit hooks
pre-commit install

# Ejecutar manualmente en todos los archivos
pre-commit run --all-files
```

## Contribuciones

¡Las contribuciones son bienvenidas! Por favor, consulta el archivo `CONTRIBUTING.md` para más detalles.

## Licencia

Este proyecto está bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.
