import json
from django.db import migrations

def load_initial_data(apps, schema_editor):
    Categoria = apps.get_model('catalogo', 'Categoria')
    Servicio = apps.get_model('catalogo', 'Servicio')
    with open('catalogo/initial_data.json', encoding='utf-8') as f:
        data = json.load(f)
        for cat in data['categorias']:
            Categoria.objects.create(**cat)
        for serv in data['servicios']:
            categoria_id = serv.pop('categoria')
            categoria = Categoria.objects.get(id=categoria_id)
            Servicio.objects.create(categoria=categoria, **serv)

class Migration(migrations.Migration):
    dependencies = [
        ('catalogo', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(load_initial_data),
    ]
