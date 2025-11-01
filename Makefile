# Makefile para Sistema de Predicción de Churn
# Facilita operaciones comunes del proyecto

.PHONY: help setup install train run api test docker-build docker-run docker-stop clean

# Variables
PYTHON := python3
PIP := pip3
STREAMLIT := streamlit
VENV := venv

# Ayuda
help:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Sistema de Predicción de Churn - Comandos Disponibles"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  Setup y Configuración:"
	@echo "    make setup          - Configuración inicial completa"
	@echo "    make install        - Instalar dependencias"
	@echo "    make venv           - Crear entorno virtual"
	@echo ""
	@echo "  Desarrollo:"
	@echo "    make train          - Entrenar modelos de ML"
	@echo "    make run            - Ejecutar dashboard Streamlit"
	@echo "    make api            - Ejecutar API REST"
	@echo "    make test           - Ejecutar tests"
	@echo "    make test-api       - Testear API REST"
	@echo ""
	@echo "  Docker:"
	@echo "    make docker-build   - Construir imagen Docker"
	@echo "    make docker-run     - Ejecutar contenedor"
	@echo "    make docker-stop    - Detener contenedor"
	@echo "    make docker-logs    - Ver logs del contenedor"
	@echo "    make docker-compose - Ejecutar con docker-compose"
	@echo ""
	@echo "  Utilidades:"
	@echo "    make clean          - Limpiar archivos temporales"
	@echo "    make lint           - Verificar código con flake8"
	@echo "    make format         - Formatear código con black"
	@echo "    make export         - Exportar clientes de alto riesgo"
	@echo ""
	@echo "════════════════════════════════════════════════════════════"

# Setup inicial completo
setup:
	@echo "🚀 Iniciando setup completo..."
	@chmod +x setup.sh
	@./setup.sh

# Crear entorno virtual
venv:
	@echo "📦 Creando entorno virtual..."
	@$(PYTHON) -m venv $(VENV)
	@echo "✅ Entorno virtual creado"
	@echo "💡 Actívalo con: source venv/bin/activate (Linux/Mac) o venv\\Scripts\\activate (Windows)"

# Instalar dependencias
install:
	@echo "📥 Instalando dependencias..."
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "✅ Dependencias instaladas"

# Entrenar modelos
train:
	@echo "🤖 Entrenando modelos de Machine Learning..."
	@$(PYTHON) train_models.py
	@echo "✅ Modelos entrenados exitosamente"

# Ejecutar dashboard
run:
	@echo "🎨 Ejecutando dashboard de Streamlit..."
	@$(STREAMLIT) run app.py

# Ejecutar en otro puerto
run-alt:
	@echo "🎨 Ejecutando dashboard en puerto 8502..."
	@$(STREAMLIT) run app.py --server.port 8502

# Ejecutar API REST
api:
	@echo "🔌 Ejecutando API REST..."
	@$(PYTHON) predict_api.py

# Ejecutar API con uvicorn (producción)
api-prod:
	@echo "🔌 Ejecutando API en modo producción..."
	@uvicorn predict_api:app --host 0.0.0.0 --port 8000 --workers 4

# Ejecutar tests
test:
	@echo "🧪 Ejecutando tests..."
	@$(PYTHON) -m pytest tests/ -v

# Test de la API
test-api:
	@echo "🧪 Testeando API REST..."
	@$(PYTHON) test_api.py

# Test de utilidades
test-utils:
	@echo "🧪 Testeando utilidades..."
	@$(PYTHON) utils.py

# Docker - Construir imagen
docker-build:
	@echo "🐳 Construyendo imagen Docker..."
	@docker build -t churn-prediction:latest .
	@echo "✅ Imagen construida: churn-prediction:latest"

# Docker - Ejecutar contenedor
docker-run:
	@echo "🐳 Ejecutando contenedor Docker..."
	@docker run -d \
		-p 8501:8501 \
		-v $$(pwd)/data:/app/data \
		-v $$(pwd)/models:/app/models \
		--name churn_dashboard \
		churn-prediction:latest
	@echo "✅ Contenedor ejecutándose en http://localhost:8501"

# Docker - Detener contenedor
docker-stop:
	@echo "🛑 Deteniendo contenedor..."
	@docker stop churn_dashboard
	@docker rm churn_dashboard
	@echo "✅ Contenedor detenido"

# Docker - Ver logs
docker-logs:
	@echo "📋 Mostrando logs del contenedor..."
	@docker logs -f churn_dashboard

# Docker Compose - Levantar servicios
docker-compose:
	@echo "🐳 Levantando servicios con Docker Compose..."
	@docker-compose up -d
	@echo "✅ Servicios activos"
	@docker-compose ps

# Docker Compose - Detener servicios
docker-compose-down:
	@echo "🛑 Deteniendo servicios..."
	@docker-compose down
	@echo "✅ Servicios detenidos"

# Docker Compose - Ver logs
docker-compose-logs:
	@docker-compose logs -f

# Docker Compose - Rebuild
docker-compose-rebuild:
	@echo "🔄 Rebuilding servicios..."
	@docker-compose up -d --build

# Limpiar archivos temporales
clean:
	@echo "🧹 Limpiando archivos temporales..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ 2>/dev/null || true
	@echo "✅ Limpieza completada"

# Limpiar todo (incluye modelos)
clean-all: clean
	@echo "🧹 Limpiando modelos y datos generados..."
	@rm -rf models/*.pkl models/*.h5 models/*.json 2>/dev/null || true
	@rm -f high_risk_customers.csv action_plan.json 2>/dev/null || true
	@echo "✅ Limpieza total completada"

# Linting con flake8
lint:
	@echo "🔍 Verificando código con flake8..."
	@$(PIP) install flake8 2>/dev/null || true
	@flake8 app.py train_models.py predict_api.py utils.py --max-line-length=120

# Formatear código con black
format:
	@echo "✨ Formateando código con black..."
	@$(PIP) install black 2>/dev/null || true
	@black app.py train_models.py predict_api.py utils.py --line-length=120

# Exportar clientes de alto riesgo
export:
	@echo "📤 Exportando clientes de alto riesgo..."
	@$(PYTHON) -c "from utils import *; df = load_dataset(); export_high_risk_customers(df)"
	@echo "✅ Exportado a high_risk_customers.csv"

# Generar reporte
report:
	@echo "📊 Generando reporte de análisis..."
	@$(PYTHON) -c "from utils import *; df = load_dataset(); print(generate_summary_report(df))"

# Análisis completo
analyze:
	@echo "🔬 Ejecutando análisis completo..."
	@$(PYTHON) -c "from utils import run_complete_analysis; run_complete_analysis()"

# Verificar requisitos
check-requirements:
	@echo "✅ Verificando requisitos del sistema..."
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "❌ Python no instalado"; exit 1; }
	@command -v $(PIP) >/dev/null 2>&1 || { echo "❌ pip no instalado"; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "⚠️  Docker no instalado (opcional)"; }
	@echo "✅ Requisitos básicos cumplidos"

# Verificar datos
check-data:
	@echo "📂 Verificando archivos de datos..."
	@test -f cleaned_data.csv && echo "✅ cleaned_data.csv encontrado" || echo "❌ cleaned_data.csv NO encontrado"
	@test -d models && echo "✅ Carpeta models/ existe" || echo "⚠️  Carpeta models/ no existe (se creará al entrenar)"
	@test -f models/random_forest_model.pkl && echo "✅ Modelos entrenados encontrados" || echo "⚠️  Modelos no entrenados (ejecuta: make train)"

# Backup de modelos
backup:
	@echo "💾 Creando backup de modelos..."
	@mkdir -p backups
	@tar -czf backups/models_backup_$$(date +%Y%m%d_%H%M%S).tar.gz models/
	@echo "✅ Backup creado en backups/"

# Restaurar último backup
restore:
	@echo "♻️  Restaurando último backup..."
	@tar -xzf $$(ls -t backups/*.tar.gz | head -1) -C .
	@echo "✅ Backup restaurado"

# Estadísticas del proyecto
stats:
	@echo "📈 Estadísticas del proyecto:"
	@echo ""
	@echo "Líneas de código Python:"
	@find . -name "*.py" -not -path "./venv/*" -exec wc -l {} + | tail -1
	@echo ""
	@echo "Archivos Python:"
	@find . -name "*.py" -not -path "./venv/*" | wc -l
	@echo ""
	@echo "Tamaño de modelos:"
	@du -sh models/ 2>/dev/null || echo "No hay modelos entrenados"

# Todo en uno: setup completo y ejecutar
all: setup train run

# Deployment checklist
deploy-check:
	@echo "✅ CHECKLIST DE DEPLOYMENT"
	@echo ""
	@test -f cleaned_data.csv && echo "✅ Datos: OK" || echo "❌ Datos: FALTA cleaned_data.csv"
	@test -f models/random_forest_model.pkl && echo "✅ Modelos: OK" || echo "❌ Modelos: FALTA entrenar"
	@test -f requirements.txt && echo "✅ Requirements: OK" || echo "❌ Requirements: FALTA"
	@test -f Dockerfile && echo "✅ Dockerfile: OK" || echo "❌ Dockerfile: FALTA"
	@test -f docker-compose.yml && echo "✅ Docker Compose: OK" || echo "❌ Docker Compose: FALTA"
	@test -f README.md && echo "✅ README: OK" || echo "❌ README: FALTA"
	@echo ""
	@echo "Para desplegar:"
	@echo "  - Local: make run"
	@echo "  - Docker: make docker-compose"
	@echo "  - Cloud: Ver DEPLOYMENT.md"

# Desarrollo rápido con auto-reload
dev:
	@echo "🔄 Modo desarrollo con auto-reload..."
	@$(STREAMLIT) run app.py --server.runOnSave true

# Versión
version:
	@echo "Sistema de Predicción de Churn v1.0"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Streamlit: $$($(STREAMLIT) --version 2>&1 | head -1)"