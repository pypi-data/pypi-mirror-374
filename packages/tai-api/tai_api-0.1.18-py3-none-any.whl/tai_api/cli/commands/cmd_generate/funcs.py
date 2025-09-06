import click
import sys
from tai_sql.generators import (
    BaseGenerator,
    ModelsGenerator,
    CRUDGenerator,
    ERDiagramGenerator
)
from tai_api.generators import RoutersGenerator, MainFileGenerator

from tai_api import ProjectConfig


def run_generate(config: ProjectConfig):
    """Run the configured generators."""
    # Ejecutar cada generador
    click.echo("🚀 Ejecutando generadores...")
    click.echo()

    models_generator = ModelsGenerator(config.database_namespace.as_posix())
    crud_generator = CRUDGenerator(
        output_dir=config.database_namespace.as_posix(),
        models_import_path=config.models_import_path,
        mode='async'
    )
    er_generator = ERDiagramGenerator(config.diagrams_namespace.as_posix())
    
    endpoints_generator = RoutersGenerator(
        output_dir=config.routers_namespace.as_posix(), 
        crud_import_path=config.crud_import_path
    )

    main_file_generator = MainFileGenerator(
        output_dir=config.main_namespace.as_posix()
    )

    generators: list[BaseGenerator] = [
        models_generator,
        crud_generator,
        er_generator,
        endpoints_generator,
        main_file_generator
    ]

    for generator in generators:
        try:
            generator_name = generator.__class__.__name__
            click.echo(f"Ejecutando: {click.style(generator_name, bold=True)}")
            
            # El generador se encargará de descubrir los modelos internamente
            result = generator.generate()
            
            click.echo(f"✅ Generador {generator_name} completado con éxito.")
            if result:
                click.echo(f"   Recursos en: {result}")
        except Exception as e:
            click.echo(f"❌ Error al ejecutar el generador {generator_name}: {str(e)}", err=True)
            sys.exit(1)
        
        finally:
            click.echo()