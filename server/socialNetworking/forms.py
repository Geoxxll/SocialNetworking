from django import forms
from .models.posts import Post
from .models.comments import Comment
from .models.authors import Author

class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=100)
    # source = forms.URLField()
    # origin = forms.URLField()
    # description = forms.CharField(widget=forms.Textarea)
    contentType = forms.ChoiceField(choices=Post.contentTypesChoices.items())
    content = forms.ImageField(required=False)  # Use ImageField for binary images
    visibility = forms.ChoiceField(choices=Post.VisibilityChoices.choices)

    class Meta:
        model = Post
        fields = ['title', 'contentType', 'visibility']
        exclude = ['origin', 'source', 'description']
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # Determine if there's initial or submitted content type
        content_type = self.initial.get('contentType') or self.data.get('contentType')
        
        if content_type in ['image/png;base64', 'image/jpeg;base64']:
            self.fields['content'] = forms.ImageField(required=False)
        else:
            self.fields['content'] = forms.FileField(required=False)
        
class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={'rows': '3', 'placeholder': 'Say Something...'})
    )

    class Meta:
        model = Comment
        fields = ['comment']  # Add the necessary fields
        widgets = {
            'comment_author': forms.HiddenInput(),  # Hide the comment_author field
            'post': forms.HiddenInput(),  # Hide the post field
        }
        
class ShareForm(forms.Form):
    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Say Something...'
            }))
    
class DraftForm(forms.ModelForm):

    class Meta:

        model = Author
        fields = [
            "id",
            "draftProfileImage",
            "draftDisplayName",
            "draftGithub"
        ]
        labels = {
            "draftProfileImage": "Profile Image",
            "draftDisplayName": "Username",
            "draftGithub": "Github"
        }
        widgets = {
            "id": forms.TextInput(attrs={"type": "hidden"}),
        }        
   
