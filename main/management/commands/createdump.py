from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Creating dump files in CSV format

    example:
    python manage.py createdump main.ItemModel main.SellerModel main.CategoryModel main.CurrencyModel
    """
    help = "Creating model's dump file"

    def add_arguments(self, parser):
        parser.add_argument('models', nargs='+', type=str)
        parser.add_argument('--output_file', type=str)

    def handle(self, *args, **options):
        models = options['models']
        output_file = options['output_file']
        output_file = output_file if output_file else 'dump.csv'

        for model in models:
            app = model.split('.')
            model_obj = getattr(__import__(app[0] + '.models', fromlist=['']), app[1])
            file_name = app[1] + '_' + output_file
            with open(file_name, 'w') as file:
                rows = model_obj.objects.all()
                all_fields = model_obj._meta.fields
                line = []
                for field in all_fields:
                    line.append(field.name)

                file.write('\t'.join(line) + '\n')

                for row in rows:
                    line.clear()
                    for field in all_fields:
                        line.append(getattr(row, field.attname))
                    file.write('\t'.join(str(value) for value in line) + '\n')
