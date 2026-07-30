const sharp = require('sharp');
const path = require('path');

const sizes = [192, 512];

async function generate() {
  for (const size of sizes) {
    await sharp(path.join(__dirname, '..', 'public', 'icons', 'icon.png'))
      .resize(size, size)
      .png()
      .toFile(path.join(__dirname, '..', 'public', 'icons', `icon-${size}.png`));
    console.log(`Generated icon-${size}.png`);
  }
}

generate().catch(console.error);




