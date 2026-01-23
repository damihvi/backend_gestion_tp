from mongoengine import Document, fields


class Linea(Document):
    """Modelo MongoDB para las líneas de transporte"""
    numero = fields.IntField(unique=True, required=True)
    nombre = fields.StringField(max_length=100, required=True)
    color = fields.StringField(max_length=50)
    descripcion = fields.StringField()

    meta = {
        'collection': 'lineas',
        'ordering': ['numero']
    }

    def __str__(self):
        return f"Línea {self.numero} - {self.nombre}"


class Parada(Document):
    """Modelo MongoDB para las paradas de transporte"""
    nombre = fields.StringField(max_length=100, required=True)
    direccion = fields.StringField(max_length=200, required=True)
    latitud = fields.DecimalField(precision=8)
    longitud = fields.DecimalField(precision=8)

    meta = {
        'collection': 'paradas',
        'ordering': ['nombre']
    }

    def __str__(self):
        return self.nombre
