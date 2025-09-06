import subprocess
import sys
import os
import shutil
from pathlib import Path
import click

from tai_api import pm, MainFileGenerator

class InitCommand:

    def __init__(self, project: str, namespace: str):
        self.project = project
        self.namespace = namespace
    
    @property
    def subnamespace(self) -> str:
        """Retorna el subnamespace basado en el namespace"""
        return self.namespace.replace('-', '_')
    
    def check_poetry(self):
        """Verifica que Poetry esté instalado y disponible"""
        try:
            subprocess.run(['poetry', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            click.echo("❌ Error: Poetry no está instalado o no está en el PATH", err=True)
            click.echo("Instala Poetry desde: https://python-poetry.org/docs/#installation")
            sys.exit(1)
    
    def check_directory_is_avaliable(self):
        """Verifica que el directorio del proyecto no exista"""
        if os.path.exists(self.namespace):
            click.echo(f"❌ Error: el directorio '{self.namespace}' ya existe", err=True)
            sys.exit(1)
    
    def check_virtualenv(self):
        """Verifica que el entorno virtual de Poetry esté activo"""
        if 'VIRTUAL_ENV' not in os.environ:
            click.echo("❌ Error: No hay entorno virutal activo", err=True)
            click.echo("   Puedes crear uno con 'pyenv virtualenv <env_name>' y asignarlo con 'pyenv local <env_name>'", err=True)
            sys.exit(1)
    
    def create_project(self):
        """Crea el proyecto base con Poetry"""
        click.echo(f"🚀 Creando '{self.namespace}'...")
        
        try:
            subprocess.run(['poetry', 'new', self.namespace], 
                        check=True, 
                        capture_output=True)
            subprocess.run(['sed', '-i', '/^python *=/d', 'pyproject.toml'], 
                        cwd=self.namespace,
                        check=True, 
                        capture_output=True)
            subprocess.run(['sed', '-i', '/\\[tool.poetry.dependencies\\]/a python = "^3.10"', 'pyproject.toml'], 
                        cwd=self.namespace,
                        check=True, 
                        capture_output=True)
            subprocess.run(['poetry', 'install'],
                        cwd=self.namespace,
                        check=True, 
                        capture_output=True)
            click.echo(f"✅ poetry new '{self.namespace}': OK")
        except subprocess.CalledProcessError as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    def create_project_config(self) -> None:
        """Crea el archivo .taisqlproject con la configuración inicial"""
        try:
            pm.create_config(
                name=self.project,
                namespace=self.namespace,
            )
            
        except Exception as e:
            click.echo(f"❌ Error al crear configuración del proyecto: {e}", err=True)
            sys.exit(1)

    def add_dependencies(self):
        """Añade las dependencias necesarias al proyecto"""
        click.echo("📦 Añadiendo dependencias...")
        
        dependencies = [
            'fastapi', 
            'uvicorn',
            'asyncpg',
            'python-jose',
            'sqlalchemy',
            'psycopg2-binary',
            'cryptography',
            'pydantic',
            'tai-alphi',
            'python-multipart',
            'fastapi-mcp'
           ]
        
        for dep in dependencies:
            try:
                subprocess.run(['poetry', 'add', dep], 
                            cwd=self.namespace,
                            check=True, 
                            capture_output=True)
                click.echo(f"   ✅ {dep} añadido")
            except subprocess.CalledProcessError as e:
                click.echo(f"   ❌ Error al añadir dependencia {dep}: {e}", err=True)
                sys.exit(1)
    
    def add_folders(self) -> None:
        """Crea la estructura adicional del proyecto"""
        test_dir = Path(self.namespace) / 'tests'
        if test_dir.exists():
            shutil.rmtree(test_dir)
        
        resources_dir = Path(__file__).parent / 'resources'

        # Crear directorio para responses
        pm.config.resources_namespace.mkdir(parents=True, exist_ok=True)
        
        if resources_dir.exists():
            # Copiar todos los archivos de la carpeta responses
            for item in resources_dir.iterdir():
                if item.is_file():
                    destination = pm.config.resources_namespace / item.name
                    shutil.copy2(item, destination)
                elif item.is_dir():
                    # Si hay subdirectorios, copiarlos recursivamente
                    destination = pm.config.resources_namespace / item.name
                    shutil.copytree(item, destination, dirs_exist_ok=True)
            
            click.echo(f"📁 Estructura responses copiada exitosamente")
        
        #Crear main file
        generator = MainFileGenerator(output_dir=pm.config.main_namespace.as_posix())
        generator.generate()

    def msg(self):
        """Muestra el mensaje de éxito y next steps con información del proyecto"""
        # ✅ Obtener información del proyecto creado
        project_root = Path(self.namespace)
        project_config = pm.load_config(project_root)
        
        click.echo()
        click.echo(f'🎉 ¡Proyecto "{self.namespace}" creado exitosamente!')
        
        # Mostrar información del proyecto
        if project_config:
            click.echo()
            click.echo("📋 Información del proyecto:")
            click.echo(f"   Nombre: {project_config.name}")
        
        click.echo()
        click.echo("📋 Próximos pasos:")
        click.echo("💡 Con tai-sql puedes definir tu schema de base de datos y con")
        click.echo("   tai-api generate crear automáticamente los routers/endpoints")
        click.echo("   asociados a ese schema.")
        click.echo()
        click.echo("🔗 Documentación: https://github.com/triplealpha-innovation/tai-sql")
        click.echo()
        click.echo("🔧 Comandos útiles:")
        click.echo("   tai-api generate                   # Generar endpoints")
        click.echo("   tai-api dev                        # Levantar servidor de desarrollo (no auth)")
        click.echo("   tai-api up                         # Levantar servidor de desarrollo (docker)")
        click.echo("   tai-api set-auth                   # Configurar autenticación")
        click.echo()
        click.echo("🔗 Documentación: https://github.com/triplealpha-innovation/tai-api")
        