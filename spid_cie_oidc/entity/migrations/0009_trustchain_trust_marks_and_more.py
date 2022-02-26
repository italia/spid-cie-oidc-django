# Generated by Django 4.0.2 on 2022-02-26 18:26

from django.db import migrations, models
import spid_cie_oidc.entity.models


class Migration(migrations.Migration):

    dependencies = [
        ('spid_cie_oidc_entity', '0008_fetchedentitystatement_jwt'),
    ]

    operations = [
        migrations.AddField(
            model_name='trustchain',
            name='trust_marks',
            field=models.JSONField(blank=True, default=list, help_text='verified trust marks'),
        ),
        migrations.AlterField(
            model_name='federationentityconfiguration',
            name='jwks',
            field=models.JSONField(default=spid_cie_oidc.entity.models.FederationEntityConfiguration._create_jwks, help_text='a list of private keys'),
        ),
    ]