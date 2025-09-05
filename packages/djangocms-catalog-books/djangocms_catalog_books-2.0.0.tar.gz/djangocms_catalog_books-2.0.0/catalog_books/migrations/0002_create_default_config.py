from django.apps import apps as django_apps
from django.db import migrations, transaction
from django.db.utils import OperationalError, ProgrammingError


def get_config_count_count(model_class):
    with transaction.atomic():
        count = model_class.objects.count()
    return count


def create_default_newsblog_config(apps, schema_editor):
    import cms.models.fields
    from cms.models import Placeholder
    CatalogBooksConfig = apps.get_model('catalog_books', 'CatalogBooksConfig')

    # if we try to execute this migration after cms migrations were migrated
    # to latest - we would get an exception because apps.get_model
    # contains cms models in the last known state (which is the dependency
    # migration state). If that is the case we need to import the real model.
    try:
        # to avoid the following error:
        #   django.db.utils.InternalError: current transaction is aborted,
        #   commands ignored until end of transaction block
        # we need to cleanup or avoid that by making transaction atomic.
        count = get_config_count_count(CatalogBooksConfig)
    except (ProgrammingError, OperationalError):
        CatalogBooksConfig = django_apps.get_model('catalog_books.CatalogBooksConfig')
        count = get_config_count_count(CatalogBooksConfig)

    if not count == 0:
        return
    # create only if there is no configs because user may already have
    # existing and configured config.
    app_config = CatalogBooksConfig(namespace='catalog_books_default', title='Catalog of Books')
    # usually generated in aldryn_apphooks_config.models.AppHookConfig
    # but in migrations we don't have real class with correct parents.
    app_config.type = 'catalog_books.cms_appconfig.CatalogBooksConfig'
    # placeholders
    # cms checks if instance.pk is set, and if it isn't cms creates a new
    # placeholder but it does that with real models, and fields on instance
    # are faked models. To prevent that we need to manually set instance pk.
    app_config.pk = 1

    for field in app_config._meta.fields:
        if not field.__class__ == cms.models.fields.PlaceholderField:
            # skip other fields.
            continue
        placeholder_name = field.name
        placeholder_id_name = f'{placeholder_name}_id'
        placeholder_id = getattr(app_config, placeholder_id_name, None)
        if placeholder_id is not None:
            # do not process if it has a reference to placeholder field.
            continue
        # since there is no placeholder - create it, we cannot use
        # get_or_create because it can get placeholder from other config
        new_placeholder = Placeholder.objects.create(
            slot=placeholder_name)
        setattr(app_config, placeholder_id_name, new_placeholder.pk)
    # after we process all placeholder fields - save config,
    # so that django can pick up them.
    app_config.save()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog_books', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_newsblog_config, lambda apps, schema_editor: None)
    ]
