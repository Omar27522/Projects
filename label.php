<?php
require 'vendor/autoload.php';

use Picqer\Barcode\BarcodeGeneratorPNG;

class LabelGenerator {
    private $dpi = 300;
    private $labelWidth;
    private $labelHeight;
    private $fontSizeLarge = 45;
    private $fontSizeMedium = 45;
    private $barcodeWidth;
    private $barcodeHeight = 310;

    public function __construct() {
        $this->labelWidth = 2 * $this->dpi;  // 600 pixels for 2 inches at 300 DPI
        $this->labelHeight = 2 * $this->dpi;  // 600 pixels for 2 inches at 300 DPI
        $this->barcodeWidth = $this->labelWidth;
    }

    public function generateBarcodeImage($upcCode) {
        $generator = new BarcodeGeneratorPNG();
        return $generator->getBarcode($upcCode, $generator::TYPE_UPC_A, 3, 100);
    }

    public function generateLabelImage($nameLine1, $nameLine2, $variant, $upcCode) {
        // Create a new image
        $labelImg = imagecreatetruecolor($this->labelWidth, $this->labelHeight);
        
        // Set background to white
        $white = imagecolorallocate($labelImg, 255, 255, 255);
        imagefill($labelImg, 0, 0, $white);
        
        // Set text color to black
        $black = imagecolorallocate($labelImg, 0, 0, 0);
        
        // Load fonts
        $fontPath = realpath('arial.ttf');
        $fontPathBold = realpath('arialbd.ttf');
        
        // Add text to image
        imagettftext($labelImg, $this->fontSizeLarge, 0, 20, 60, $black, $fontPathBold, $nameLine1);
        
        if (!empty($nameLine2)) {
            imagettftext($labelImg, $this->fontSizeLarge, 0, 20, 120, $black, $fontPathBold, $nameLine2);
        }
        
        // Add variant text (centered)
        $variantBox = imagettfbbox($this->fontSizeMedium, 0, $fontPath, $variant);
        $variantWidth = $variantBox[2] - $variantBox[0];
        $variantX = ($this->labelWidth - $variantWidth) / 2;
        imagettftext($labelImg, $this->fontSizeMedium, 0, $variantX, 230, $black, $fontPath, $variant);
        
        // Generate and add barcode
        $barcodeData = $this->generateBarcodeImage($upcCode);
        $barcodeImg = imagecreatefromstring($barcodeData);
        
        // Resize barcode
        $resizedBarcode = imagecreatetruecolor($this->barcodeWidth, $this->barcodeHeight);
        imagecopyresampled(
            $resizedBarcode, $barcodeImg,
            0, 0, 0, 0,
            $this->barcodeWidth, $this->barcodeHeight,
            imagesx($barcodeImg), imagesy($barcodeImg)
        );
        
        // Add barcode to label
        $barcodeX = ($this->labelWidth - $this->barcodeWidth) / 2;
        imagecopy($labelImg, $resizedBarcode, $barcodeX, 310, 0, 0, $this->barcodeWidth, $this->barcodeHeight);
        
        // Clean up
        imagedestroy($barcodeImg);
        imagedestroy($resizedBarcode);
        
        return $labelImg;
    }

    public function outputLabel($labelImg) {
        header('Content-Type: image/png');
        imagepng($labelImg);
        imagedestroy($labelImg);
    }
}

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $generator = new LabelGenerator();
    
    $nameLine1 = $_POST['name_line1'] ?? '';
    $nameLine2 = $_POST['name_line2'] ?? '';
    $variant = $_POST['variant'] ?? '';
    $upcCode = $_POST['upc_code'] ?? '';
    
    if (!empty($nameLine1) && !empty($variant) && !empty($upcCode) && 
        strlen($upcCode) === 12 && ctype_digit($upcCode)) {
        
        $labelImg = $generator->generateLabelImage($nameLine1, $nameLine2, $variant, $upcCode);
        $generator->outputLabel($labelImg);
        exit;
    }
}
?>
