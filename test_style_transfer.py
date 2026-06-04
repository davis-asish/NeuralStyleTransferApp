import os
import requests
from PIL import Image
import io

# Test script for Neural Style Transfer Application

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://127.0.0.1:5000/health')
        print(f"Health check status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_generate_content():
    """Test content image generation"""
    try:
        payload = {"prompt": "a beautiful mountain landscape"}
        response = requests.post('http://127.0.0.1:5000/generate', json=payload, timeout=600)  # 10 minute timeout
        print(f"Generate content status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'image_url' in data:
                print(f"Generated content image: {data['image_url']}")
                return True
            else:
                print(f"Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"Error response: {response.text}")
        return False
    except requests.exceptions.Timeout:
        print("Generate content timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"Generate content failed: {e}")
        return False

def test_generate_style():
    """Test style image generation"""
    try:
        payload = {"prompt": "abstract art in blue and green tones"}
        response = requests.post('http://127.0.0.1:5000/generate', json=payload, timeout=600)  # 10 minute timeout
        print(f"Generate style status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'image_url' in data:
                print(f"Generated style image: {data['image_url']}")
                return True
            else:
                print(f"Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"Error response: {response.text}")
        return False
    except requests.exceptions.Timeout:
        print("Generate style timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"Generate style failed: {e}")
        return False

def test_style_transfer():
    """Test style transfer using Stable Diffusion img2img"""
    try:
        from backend.sd_utils import stylize_image
        import os

        # Create sample content image for testing
        content_img = Image.new('RGB', (256, 256), color='red')
        content_path = 'test_content.png'
        content_img.save(content_path)

        # Test style transfer
        output_path = stylize_image(content_path, "anime", output_path="outputs/test_styled.png")

        if output_path and os.path.exists(output_path):
            print(f"Style transfer successful: {output_path}")
            # Cleanup
            os.remove(content_path)
            return True
        else:
            print("Style transfer failed: output file not created")
            # Cleanup
            if os.path.exists(content_path):
                os.remove(content_path)
            return False
    except Exception as e:
        print(f"Style transfer failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Neural Style Transfer Application")
    print("=" * 50)

    # Test health check
    print("\n1. Testing health check...")
    health_ok = test_health_check()

    # Test image generation (may fail if Ollama not running)
    print("\n2. Testing content generation...")
    content_ok = test_generate_content()

    print("\n3. Testing style generation...")
    style_ok = test_generate_style()

    # Test style transfer
    print("\n4. Testing style transfer...")
    transfer_ok = test_style_transfer()

    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Health Check: {'PASS' if health_ok else 'FAIL'}")
    print(f"Content Generation: {'PASS' if content_ok else 'FAIL'}")
    print(f"Style Generation: {'PASS' if style_ok else 'FAIL'}")
    print(f"Style Transfer: {'PASS' if transfer_ok else 'FAIL'}")

if __name__ == '__main__':
    main()
