# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Commands(models.Model):
    command = models.TextField(blank=True, null=True)
    technique = models.ForeignKey('Techniques', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'commands'


class Reasons(models.Model):
    tactic = models.ForeignKey('Tactics', models.DO_NOTHING, blank=True, null=True)
    technique = models.ForeignKey('Techniques', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reasons'


class Tactics(models.Model):
    external_id = models.CharField(unique=True, max_length=6)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tactics'


class Techniques(models.Model):
    external_id = models.CharField(unique=True, max_length=9)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_subtechnique = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'techniques'