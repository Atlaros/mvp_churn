"""
Script Mejorado para Ejecutar el Proyecto Completo
Verifica dependencias, modelos y ejecuta el dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    """Imprime encabezado bonito"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def check_python_version():
    """Verifica versión de Python"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    
    if version.major == 3 and version.minor >= 10:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} - Se requiere Python 3.10+")
        return False

def check_venv():
    """Verifica si está en entorno virtual"""
    print("\n📦 Verificando entorno virtual...")
    
    # Verificar si ya está en venv
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        print("   ✅ Entorno virtual activo")
        return True
    else:
        # Buscar si existe venv pero no está activado
        venv_paths = [
            Path('venv/Scripts/activate.bat'),
            Path('.venv/Scripts/activate.bat'),
            Path('venv/bin/activate'),
            Path('.venv/bin/activate')
        ]
        
        venv_found = None
        for venv_path in venv_paths:
            if venv_path.exists():
                venv_found = venv_path
                break
        
        if venv_found:
            print(f"   ⚠️  Entorno virtual encontrado pero NO activo: {venv_found.parent.parent}")
            print(f"   💡 Para activar:")
            if os.name == 'nt':  # Windows
                print(f"      {venv_found.parent.parent}\\Scripts\\activate.bat")
            else:  # Linux/Mac
                print(f"      source {venv_found.parent.parent}/bin/activate")
            print("\n   💡 O usa los scripts con venv:")
            print("      - EJECUTAR_CON_VENV.bat (Windows)")
            print("      - ejecutar_venv.ps1 (PowerShell)")
        else:
            print("   ⚠️  No hay entorno virtual creado")
            print("   💡 Para crear uno:")
            print("      python -m venv venv")
        
        return True  # No bloqueante

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print("\n📚 Verificando dependencias...")
    
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'scikit-learn',
        'xgboost',
        'tensorflow',
        'shap',
        'mlflow',
        'reportlab'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NO INSTALADO")
            missing.append(package)
    
    if missing:
        print(f"\n   ⚠️  Faltan {len(missing)} paquetes")
        print(f"\n   Para instalar, ejecuta:")
        print(f"   pip install -r requirements.txt")
        return False
    
    print("\n   ✅ Todas las dependencias instaladas")
    return True

def check_data():
    """Verifica que existan los datos"""
    print("\n📊 Verificando datos...")
    
    if Path('cleaned_data.csv').exists():
        size_mb = Path('cleaned_data.csv').stat().st_size / 1024 / 1024
        print(f"   ✅ cleaned_data.csv ({size_mb:.1f} MB)")
        return True
    else:
        print("   ❌ cleaned_data.csv NO ENCONTRADO")
        print("   Coloca el archivo en la raíz del proyecto")
        return False

def check_models():
    """Verifica que existan los modelos"""
    print("\n🤖 Verificando modelos...")
    
    model_files = [
        'models/random_forest_model.pkl',
        'models/xgboost_model.pkl',
        'models/scaler.pkl',
        'models/label_encoders.pkl'
    ]
    
    all_exist = True
    for model_file in model_files:
        if Path(model_file).exists():
            print(f"   ✅ {model_file}")
        else:
            print(f"   ❌ {model_file} - NO ENCONTRADO")
            all_exist = False
    
    if not all_exist:
        print("\n   ⚠️  Algunos modelos no encontrados")
        print("   Para entrenar los modelos, ejecuta:")
        print("   python train_models.py")
        print("\n   O con MLflow:")
        print("   python train_models_mlflow.py")
        return False
    
    print("\n   ✅ Todos los modelos disponibles")
    return True

def create_directories():
    """Crea directorios necesarios"""
    print("\n📁 Verificando directorios...")
    
    dirs = ['logs', 'models/backups', 'mlruns']
    
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}/")
    
    return True

def show_options():
    """Muestra opciones de ejecución"""
    print_header("OPCIONES DE EJECUCIÓN")
    
    print("Selecciona qué ejecutar:\n")
    print("1. 🎨 Dashboard Principal (Streamlit)")
    print("2. 🔌 API REST (FastAPI)")
    print("3. 📊 MLflow UI (Ver experimentos)")
    print("4. 🔄 Entrenar Modelos")
    print("5. 🔄 Entrenar con MLflow")
    print("6. ✅ Verificar Todo y Salir")
    print("0. ❌ Salir\n")
    
    return input("Opción: ").strip()

def run_streamlit():
    """Ejecuta el dashboard de Streamlit"""
    print_header("EJECUTANDO DASHBOARD STREAMLIT")
    
    print("🚀 Iniciando Streamlit...")
    print("📍 URL: http://localhost:8501")
    print("\n⏹️  Para detener: Ctrl+C\n")
    print("-"*70 + "\n")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', '8501',
            '--server.address', 'localhost'
        ])
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard detenido")

def run_api():
    """Ejecuta la API FastAPI"""
    print_header("EJECUTANDO API REST")
    
    print("🚀 Iniciando FastAPI...")
    print("📍 URL: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("\n⏹️  Para detener: Ctrl+C\n")
    print("-"*70 + "\n")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 'predict_api:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ])
    except KeyboardInterrupt:
        print("\n\n✅ API detenida")

def run_mlflow_ui():
    """Ejecuta MLflow UI"""
    print_header("EJECUTANDO MLFLOW UI")
    
    print("🚀 Iniciando MLflow UI...")
    print("📍 URL: http://localhost:5000")
    print("\n⏹️  Para detener: Ctrl+C\n")
    print("-"*70 + "\n")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'mlflow', 'ui'
        ])
    except KeyboardInterrupt:
        print("\n\n✅ MLflow UI detenido")

def run_training():
    """Ejecuta entrenamiento de modelos"""
    print_header("ENTRENANDO MODELOS")
    
    print("🤖 Entrenando Random Forest, XGBoost y Red Neuronal...")
    print("⏱️  Esto puede tomar 5-10 minutos\n")
    print("-"*70 + "\n")
    
    subprocess.run([sys.executable, 'train_models.py'])
    
    print("\n✅ Entrenamiento completado")
    input("\nPresiona Enter para continuar...")

def run_training_mlflow():
    """Ejecuta entrenamiento con MLflow"""
    print_header("ENTRENANDO MODELOS CON MLFLOW")
    
    print("🤖 Entrenando con tracking de MLflow...")
    print("⏱️  Esto puede tomar 5-10 minutos\n")
    print("-"*70 + "\n")
    
    subprocess.run([sys.executable, 'train_models_mlflow.py'])
    
    print("\n✅ Entrenamiento completado")
    print("💡 Para ver resultados: python EJECUTAR_PROYECTO.py → Opción 3")
    input("\nPresiona Enter para continuar...")

def main():
    """Función principal"""
    print_header("🚀 SISTEMA DE PREDICCIÓN DE CHURN")
    
    # Verificaciones
    checks = {
        'Python': check_python_version(),
        'Venv': check_venv(),
        'Dependencias': check_dependencies(),
        'Datos': check_data(),
        'Modelos': check_models(),
        'Directorios': create_directories()
    }
    
    # Resumen de verificaciones
    print("\n" + "="*70)
    print("  RESUMEN DE VERIFICACIONES")
    print("="*70 + "\n")
    
    for check_name, status in checks.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {check_name}")
    
    # Si faltan cosas críticas
    if not checks['Python']:
        print("\n❌ ERROR CRÍTICO: Versión de Python incompatible")
        print("   Instala Python 3.10+ desde: https://www.python.org/downloads/")
        input("\nPresiona Enter para salir...")
        return
    
    if not checks['Dependencias']:
        print("\n⚠️  ADVERTENCIA: Faltan dependencias")
        print("   Instala con: pip install -r requirements.txt")
        
        response = input("\n¿Instalar ahora? (s/n): ").lower()
        if response == 's':
            print("\n📦 Instalando dependencias...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("\n✅ Dependencias instaladas")
        else:
            print("\n⚠️  Algunas funcionalidades pueden no funcionar")
    
    if not checks['Datos']:
        print("\n❌ ERROR: Sin datos no se puede ejecutar")
        print("   Coloca 'cleaned_data.csv' en la raíz del proyecto")
        input("\nPresiona Enter para salir...")
        return
    
    if not checks['Modelos']:
        print("\n⚠️  ADVERTENCIA: Modelos no encontrados")
        
        response = input("\n¿Entrenar modelos ahora? (s/n): ").lower()
        if response == 's':
            run_training()
    
    # Loop principal
    while True:
        option = show_options()
        
        if option == '1':
            run_streamlit()
        elif option == '2':
            run_api()
        elif option == '3':
            run_mlflow_ui()
        elif option == '4':
            run_training()
        elif option == '5':
            run_training_mlflow()
        elif option == '6':
            print("\n✅ Verificación completa")
            break
        elif option == '0':
            print("\n👋 ¡Hasta pronto!")
            break
        else:
            print("\n❌ Opción inválida")
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Ejecución cancelada por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPresiona Enter para salir...")
