from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transporte', '0003_remove_userprofile_is_conductor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiculo',
            name='linea',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehiculos', to='transporte.linea'),
        ),
    ]
