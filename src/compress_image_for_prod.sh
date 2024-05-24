# Go through images in image/ directory.
# Ignore the ones that end with a numeric suffix (meaning they are not selected).
# Compress these images and save them to the specified directory.

# Get the output path.
output_path=$1

# If no output path is specified, fail.
if [ -z "$output_path" ]; then
  echo "Usage: compress_image_for_prod.sh <output_path>"
  exit 1
fi

mkdir -p $output_path

for file in images/*; do
  # Check if the file ends with a number.
  file_no_ext=$(basename $file .jpg)
  if [[ $file_no_ext =~ [0-9]$ ]]; then
    echo "Skipping $file"
    continue
  fi

  # Get the base name of the file.
  output_file=$(basename $file)
  # Compress the image and save it to the specified directory.
  convert $file -resize 480x480 -quality 75 $output_path/$output_file
done
