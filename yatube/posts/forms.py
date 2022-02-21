from django.forms import ModelForm
from django.core.exceptions import ValidationError

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise ValidationError
        return data
