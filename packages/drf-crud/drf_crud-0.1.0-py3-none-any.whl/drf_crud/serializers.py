from rest_framework import serializers

def generate_serializer(model, fields="__all__"):
    """
    Dynamically generate a ModelSerializer for the given model.
    """
    m = model
    f = fields
    class AutoSerializer(serializers.ModelSerializer):
        class Meta:
            model = m
            fields = f
    return AutoSerializer
