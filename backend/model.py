import torch  # PyTorch library for tensor computations and neural networks
import torch.nn as nn  # Neural network modules
import torch.optim as optim  # Optimization algorithms
from torchvision import models  # Pre-trained models
import torchvision.transforms as transforms  # Image transformations
from PIL import Image  # Image processing library
import numpy as np  # Numerical operations
import logging  # Logging for debugging and monitoring

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Device configuration: Use GPU if available, else CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

# Load pre-trained VGG19 model
vgg = models.vgg19(pretrained=True).features.to(device).eval()
logger.info("VGG19 model loaded")

# Define layers for content and style extraction
content_layers = ['conv_4']  # Layer for content features
style_layers = ['conv_1', 'conv_2', 'conv_3', 'conv_4', 'conv_5']  # Layers for style features

def get_features(image, model, layers):
    # Function to extract features from specified layers
    features = {}
    x = image
    for name, layer in model._modules.items():
        x = layer(x)
        if name in layers:
            features[name] = x
    return features

def gram_matrix(tensor):
    # Compute Gram matrix for style representation
    _, d, h, w = tensor.size()
    tensor = tensor.view(d, h * w)
    gram = torch.mm(tensor, tensor.t())
    return gram

class StyleTransfer:
    def __init__(self, content_image, style_images, num_steps=300, style_weight=1e6, content_weight=1):
        self.content_image = self.load_image(content_image).to(device)
        self.style_images = [self.load_image(img).to(device) for img in style_images]
        self.num_steps = num_steps
        self.style_weight = style_weight
        self.content_weight = content_weight
        self.generated = self.content_image.clone().requires_grad_(True).to(device)

    def load_image(self, img_path, max_size=400):
        # Load and preprocess image
        image = Image.open(img_path).convert('RGB')
        size = max(image.size)
        if size > max_size:
            size = max_size
        image = transforms.Compose([
            transforms.Resize(size),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
        ])(image).unsqueeze(0)
        return image

    def compute_content_loss(self, gen_features, content_features):
        # Compute content loss
        return torch.mean((gen_features['conv_4'] - content_features['conv_4']) ** 2)

    def compute_style_loss(self, gen_features, style_features):
        # Compute style loss for a single style
        loss = 0
        for layer in style_layers:
            gen_gram = gram_matrix(gen_features[layer])
            style_gram = gram_matrix(style_features[layer])
            layer_loss = torch.mean((gen_gram - style_gram) ** 2)
            loss += layer_loss
        return loss

    def compute_total_loss(self, gen_features, content_features, style_features_list):
        # Compute total loss including content and style(s)
        content_loss = self.compute_content_loss(gen_features, content_features)
        style_loss = 0
        for style_features in style_features_list:
            style_loss += self.compute_style_loss(gen_features, style_features)
        style_loss /= len(style_features_list)  # Average if multiple styles
        total_loss = self.content_weight * content_loss + self.style_weight * style_loss
        return total_loss, content_loss, style_loss

    def transfer_style(self):
        # Main style transfer function
        optimizer = optim.LBFGS([self.generated], max_iter=self.num_steps)
        content_features = get_features(self.content_image, vgg, content_layers)
        style_features_list = [get_features(style_img, vgg, style_layers) for style_img in self.style_images]

        def closure():
            optimizer.zero_grad()
            gen_features = get_features(self.generated, vgg, content_layers + style_layers)
            total_loss, content_loss, style_loss = self.compute_total_loss(gen_features, content_features, style_features_list)
            total_loss.backward()
            logger.info(f"Step: Loss: {total_loss.item():.4f}, Content: {content_loss.item():.4f}, Style: {style_loss.item():.4f}")
            return total_loss

        optimizer.step(closure)
        return self.generated

def save_image(tensor, path):
    # Save tensor as image
    image = tensor.cpu().clone()
    image = image.squeeze(0)
    image = transforms.ToPILImage()(image)
    image.save(path)
    logger.info(f"Image saved to {path}")

# Function to perform style transfer
def perform_style_transfer(content_path, style_paths, output_path, num_steps=300):
    # Main entry point for style transfer
    st = StyleTransfer(content_path, style_paths, num_steps=num_steps)
    result = st.transfer_style()
    save_image(result, output_path)
    return output_path
