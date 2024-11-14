#!/bin/zsh

# converts spigot/paper worlds to vanilla
# have world, world_nether, world_the_end inside folder 
# have folder in BASE_DIR

# set the processing directory containing world folders
BASE_DIR=""

# iterate through each subdirectory in the base directory
for dir in "$BASE_DIR"/*(/); do
  echo "Processing folder: $dir"

  WORLD_DIR="${dir}/world"
  NETHER_DIR="${dir}/world_nether"
  END_DIR="${dir}/world_the_end"

  # check if the nether and end folders exist
  if [[ -d "$NETHER_DIR" && -d "$END_DIR" ]]; then
    cp -r "$NETHER_DIR"/DIM* "$WORLD_DIR" 2>/dev/null
    echo "Copied DIM* from $NETHER_DIR to $WORLD_DIR"

    cp -r "$END_DIR"/DIM* "$WORLD_DIR" 2>/dev/null
    echo "Copied DIM* from $END_DIR to $WORLD_DIR"

    rm -rf "$NETHER_DIR" "$END_DIR"
    echo "Deleted $NETHER_DIR and $END_DIR"
  else
    echo "One or both of the folders $NETHER_DIR or $END_DIR do not exist, skipping."
  fi

  echo "Done processing $dir"
  echo "---------------------------------"
done

echo "All folders processed."
