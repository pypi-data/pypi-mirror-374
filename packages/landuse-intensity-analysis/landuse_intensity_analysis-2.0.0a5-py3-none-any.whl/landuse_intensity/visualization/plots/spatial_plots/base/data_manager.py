"""
Geospatial data management component.

This module provides utilities for loading, validating, and managing
geospatial data used in spatial analysis operations.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import numpy as np
import warnings

# Import geospatial libraries with fallback
try:
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import calculate_default_transform, reproject
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False
    rasterio = None


class GeospatialDataManager:
    """
    Manager for geospatial data operations.
    
    This class handles loading, validation, stacking, and saving of
    geospatial raster data with support for multiple formats and
    coordinate systems.
    
    Attributes
    ----------
    reference_meta : Dict[str, Any]
        Reference metadata from the first loaded image
    loaded_images : Dict[str, np.ndarray]
        Cache of loaded images
    """
    
    def __init__(self):
        """Initialize the data manager."""
        self.reference_meta = None
        self.loaded_images = {}
        self._validated = False
        
    def load_and_validate(self, 
                         images_data: Dict[str, Union[str, np.ndarray]]) -> Dict[str, Any]:
        """
        Load and validate all input images.
        
        Parameters
        ----------
        images_data : Dict[str, Union[str, np.ndarray]]
            Dictionary with year keys and file paths or arrays as values
            
        Returns
        -------
        Dict[str, Any]
            Dictionary containing loaded images, metadata, and validation info
        """
        print(f"📚 Loading and validating {len(images_data)} images...")
        
        loaded_data = {
            'images': {},
            'metadata': {},
            'validation': {},
            'sorted_years': sorted(images_data.keys())
        }
        
        # Load all images
        for year in loaded_data['sorted_years']:
            image_data = self._load_single_image(year, images_data[year])
            loaded_data['images'][year] = image_data
            
        # Validate consistency
        validation_result = self._validate_images(loaded_data['images'])
        loaded_data['validation'] = validation_result
        
        # Store metadata
        if self.reference_meta:
            loaded_data['metadata'] = self.reference_meta.copy()
            
        # Create image stack
        loaded_data['image_stack'] = self._create_image_stack(
            loaded_data['images'], 
            loaded_data['sorted_years']
        )
        
        print(f"✅ Successfully loaded {len(loaded_data['images'])} images")
        return loaded_data
        
    def _load_single_image(self, 
                          year: str, 
                          image_source: Union[str, np.ndarray]) -> np.ndarray:
        """
        Load a single image from file path or array.
        
        Parameters
        ----------
        year : str
            Year identifier
        image_source : Union[str, np.ndarray]
            File path or numpy array
            
        Returns
        -------
        np.ndarray
            Loaded image data
        """
        if isinstance(image_source, str):
            return self._load_from_file(year, image_source)
        elif isinstance(image_source, np.ndarray):
            return self._load_from_array(year, image_source)
        else:
            raise ValueError(f"Invalid image source type for year {year}: {type(image_source)}")
            
    def _load_from_file(self, year: str, file_path: str) -> np.ndarray:
        """Load image from file path."""
        if not HAS_RASTERIO:
            raise ImportError("rasterio is required for loading geospatial files")
            
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found for year {year}: {file_path}")
            
        try:
            with rasterio.open(file_path) as src:
                data = src.read(1)  # Read first band
                
                # Store reference metadata from first image
                if self.reference_meta is None:
                    self.reference_meta = src.meta.copy()
                    
                return data
                
        except Exception as e:
            raise RuntimeError(f"Failed to load image for year {year}: {e}")
            
    def _load_from_array(self, year: str, array: np.ndarray) -> np.ndarray:
        """Load image from numpy array."""
        if array.ndim < 2:
            raise ValueError(f"Array for year {year} must be at least 2D")
            
        # Take first 2D slice if 3D
        if array.ndim == 3:
            array = array[0] if array.shape[0] == 1 else array[:, :, 0]
            
        return array.astype(np.int32)  # Ensure consistent dtype
        
    def _validate_images(self, images: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Validate consistency across all loaded images.
        
        Parameters
        ----------
        images : Dict[str, np.ndarray]
            Dictionary of loaded images
            
        Returns
        -------
        Dict[str, Any]
            Validation results and warnings
        """
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'shapes': {},
            'dtypes': {},
            'value_ranges': {}
        }
        
        if not images:
            validation_result['is_valid'] = False
            validation_result['errors'].append("No images provided")
            return validation_result
            
        # Check shapes consistency
        shapes = {year: img.shape for year, img in images.items()}
        validation_result['shapes'] = shapes
        
        reference_shape = next(iter(shapes.values()))
        inconsistent_shapes = {year: shape for year, shape in shapes.items() 
                             if shape != reference_shape}
        
        if inconsistent_shapes:
            warning_msg = f"Inconsistent image shapes detected: {inconsistent_shapes}"
            validation_result['warnings'].append(warning_msg)
            warnings.warn(warning_msg)
            
        # Check data types
        dtypes = {year: str(img.dtype) for year, img in images.items()}
        validation_result['dtypes'] = dtypes
        
        # Check value ranges
        value_ranges = {}
        for year, img in images.items():
            value_ranges[year] = {
                'min': int(np.min(img)),
                'max': int(np.max(img)),
                'unique_count': len(np.unique(img))
            }
        validation_result['value_ranges'] = value_ranges
        
        return validation_result
        
    def _create_image_stack(self, 
                           images: Dict[str, np.ndarray], 
                           sorted_years: List[str]) -> np.ndarray:
        """
        Create 3D image stack [time, row, col].
        
        Parameters
        ----------
        images : Dict[str, np.ndarray]
            Dictionary of loaded images
        sorted_years : List[str]
            Sorted list of years
            
        Returns
        -------
        np.ndarray
            3D array with shape [time, row, col]
        """
        if not images:
            return np.array([])
            
        # Get reference shape
        reference_shape = next(iter(images.values())).shape
        
        # Create stack
        image_list = []
        for year in sorted_years:
            img = images[year]
            
            # Ensure consistent shape (pad or crop if necessary)
            if img.shape != reference_shape:
                img = self._normalize_image_shape(img, reference_shape)
                
            image_list.append(img)
            
        image_stack = np.stack(image_list, axis=0)
        print(f"📐 Created image stack with shape: {image_stack.shape}")
        
        return image_stack
        
    def _normalize_image_shape(self, 
                             image: np.ndarray, 
                             target_shape: Tuple[int, int]) -> np.ndarray:
        """
        Normalize image shape to match target shape.
        
        Parameters
        ----------
        image : np.ndarray
            Input image
        target_shape : Tuple[int, int]
            Target shape (rows, cols)
            
        Returns
        -------
        np.ndarray
            Normalized image
        """
        current_shape = image.shape
        target_rows, target_cols = target_shape
        
        # Pad or crop as needed
        if current_shape[0] < target_rows or current_shape[1] < target_cols:
            # Pad if smaller
            pad_rows = max(0, target_rows - current_shape[0])
            pad_cols = max(0, target_cols - current_shape[1])
            image = np.pad(image, ((0, pad_rows), (0, pad_cols)), 
                          mode='constant', constant_values=0)
        
        if current_shape[0] > target_rows or current_shape[1] > target_cols:
            # Crop if larger
            image = image[:target_rows, :target_cols]
            
        return image
        
    def save_geotiff(self, 
                    data: np.ndarray, 
                    output_path: Path,
                    **kwargs) -> Optional[Path]:
        """
        Save data as GeoTIFF using reference metadata.
        
        Parameters
        ----------
        data : np.ndarray
            Data to save
        output_path : Path
            Output file path
        **kwargs
            Additional parameters
            
        Returns
        -------
        Optional[Path]
            Output path if successful, None otherwise
        """
        if not HAS_RASTERIO:
            print("⚠️ rasterio not available - cannot save GeoTIFF")
            return None
            
        if self.reference_meta is None:
            print("⚠️ No reference metadata available - cannot save GeoTIFF")
            return None
            
        try:
            # Prepare metadata
            output_meta = self.reference_meta.copy()
            output_meta.update({
                'dtype': data.dtype,
                'count': 1,
                'compress': 'lzw'
            })
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file
            with rasterio.open(output_path, 'w', **output_meta) as dst:
                dst.write(data, 1)
                
            print(f"💾 Saved GeoTIFF: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"⚠️ Could not save GeoTIFF: {e}")
            return None
            
    def get_unique_classes(self, 
                          images: Dict[str, np.ndarray], 
                          exclude_nodata: bool = True) -> np.ndarray:
        """
        Get unique classes across all images.
        
        Parameters
        ----------
        images : Dict[str, np.ndarray]
            Dictionary of images
        exclude_nodata : bool
            Whether to exclude nodata values (0)
            
        Returns
        -------
        np.ndarray
            Array of unique class values
        """
        all_values = []
        for img in images.values():
            all_values.extend(img.flatten())
            
        unique_values = np.unique(all_values)
        
        if exclude_nodata:
            unique_values = unique_values[unique_values != 0]
            
        return unique_values
        
    def calculate_valid_mask(self, image_stack: np.ndarray) -> np.ndarray:
        """
        Calculate mask for valid pixels across all images.
        
        Parameters
        ----------
        image_stack : np.ndarray
            3D image stack [time, row, col]
            
        Returns
        -------
        np.ndarray
            Boolean mask for valid pixels
        """
        if image_stack.size == 0:
            return np.array([])
            
        # Valid pixels are non-zero in all time steps
        valid_mask = np.all(image_stack != 0, axis=0)
        return valid_mask
        
    def get_statistics_summary(self, 
                             images: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Get comprehensive statistics summary for all images.
        
        Parameters
        ----------
        images : Dict[str, np.ndarray]
            Dictionary of images
            
        Returns
        -------
        Dict[str, Any]
            Statistics summary
        """
        summary = {
            'total_images': len(images),
            'year_range': f"{min(images.keys())}-{max(images.keys())}" if images else "None",
            'per_image_stats': {},
            'overall_stats': {}
        }
        
        # Per-image statistics
        for year, img in images.items():
            summary['per_image_stats'][year] = {
                'shape': img.shape,
                'dtype': str(img.dtype),
                'min': int(np.min(img)),
                'max': int(np.max(img)),
                'mean': float(np.mean(img)),
                'std': float(np.std(img)),
                'unique_values': len(np.unique(img)),
                'valid_pixels': int(np.sum(img != 0)),
                'total_pixels': int(img.size)
            }
            
        # Overall statistics
        if images:
            all_data = np.concatenate([img.flatten() for img in images.values()])
            summary['overall_stats'] = {
                'total_pixels': len(all_data),
                'min': int(np.min(all_data)),
                'max': int(np.max(all_data)),
                'mean': float(np.mean(all_data)),
                'std': float(np.std(all_data)),
                'unique_values': len(np.unique(all_data))
            }
            
        return summary
