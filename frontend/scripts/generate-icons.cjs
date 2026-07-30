const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const sizes = [192, 512];
const svgPath = path.join(__dirname, '..', 'public', 'icons', 'icon.svg');
const svg = fs.readFileSync(svgPath, 'utf-8');

async function generate() {
  for (const size of sizes) {
    await sharp(Buffer.from(svg))
      .resize(size, size)
      .png()
      .toFile(path.join(__dirname, '..', 'public', 'icons', `icon-${size}.png`));
    console.log(`Generated icon-${size}.png`);
  }
}

generate().catch(console.error);
