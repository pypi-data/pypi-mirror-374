/*
Project: thormotion
GitHub: https://github.com/MillieFD/thormotion

BSD 3-Clause License, Copyright (c) 2025, Amelia Fraser-Dale

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the conditions of the LICENSE are met.
*/

use std::ops::Deref;

pub(crate) enum Units {
    Distance([u8; 4]),
    Velocity([u8; 4]),
    Acceleration([u8; 4]),
}

impl Units {
    /// Converts a slice `&[u8]` into an array `[u8; N]`.
    #[doc(hidden)]
    #[inline]
    fn array_from_slice<const N: usize>(slice: &[u8]) -> [u8; N] {
        let mut array = [0u8; N];
        for (i, &byte) in slice.iter().take(N).enumerate() {
            array[i] = byte;
        }
        array
    }

    /// Constructs a new [`Units::Distance`] from device units.
    ///
    /// ### Aborts
    ///
    /// This function aborts if the slice cannot be coerced into a four-byte array `[u8; 4]`
    pub(crate) fn distance_from_slice(slice: &[u8]) -> Units {
        Units::Distance(Units::array_from_slice(slice))
    }

    /// Constructs a new [`Units::Velocity`] from device units.
    ///
    /// ### Aborts
    ///
    /// This function aborts if the slice cannot be coerced into a four-byte array `[u8; 4]`
    pub(crate) fn velocity_from_slice(slice: &[u8]) -> Units {
        Units::Velocity(Units::array_from_slice(slice))
    }

    /// Constructs a new [`Units::Acceleration`] from device units.
    ///
    /// ### Aborts
    ///
    /// This function aborts if the slice cannot be coerced into a four-byte array `[u8; 4]`
    pub(crate) fn acceleration_from_slice(slice: &[u8]) -> Units {
        Units::Acceleration(Units::array_from_slice(slice))
    }

    /// Converts an `f64` to an unwrapped little-endian byte array `[u8; 4]`.
    ///
    /// You can manually wrap the result in the appropriate [`Units`] variant. To automatically wrap
    /// the result, see the [`new_distance`][1], [`new_velocity`][2], and [`new_acceleration`][3]
    /// functions.
    ///
    /// [1]: Units::distance_from_f64
    /// [2]: Units::velocity_from_f64
    /// [3]: Units::acceleration_from_f64
    fn encode(value: f64, scale_factor: f64) -> [u8; 4] {
        let scaled = value * scale_factor;
        let rounded = scaled.round() as i32;
        i32::to_le_bytes(rounded)
    }

    /// Converts a distance (millimeters) or angle (degrees) from real-world units to device units
    /// using the appropriate [`scale factor`][1].
    ///
    /// [1]: UnitConversion::DISTANCE_ANGLE_SCALE_FACTOR
    pub(crate) fn distance_from_f64<A>(distance: f64) -> Units
    where
        A: UnitConversion,
    {
        let bytes = Units::encode(distance, A::DISTANCE_ANGLE_SCALE_FACTOR);
        Units::Distance(bytes)
    }

    /// Converts a velocity from real-world units (mm/s) to device units using the appropriate
    /// [`scale factor`][1].
    ///
    /// [1]: UnitConversion::VELOCITY_SCALE_FACTOR
    pub(crate) fn velocity_from_f64<A>(velocity: f64) -> Units
    where
        A: UnitConversion,
    {
        let bytes = Units::encode(velocity, A::VELOCITY_SCALE_FACTOR);
        Units::Distance(bytes)
    }

    /// Converts an acceleration from real-world units (mm/s²) to device units using the appropriate
    /// [`scale factor`][1].
    ///
    /// [1]: UnitConversion::ACCELERATION_SCALE_FACTOR
    pub(crate) fn acceleration_from_f64<A>(acceleration: f64) -> Units
    where
        A: UnitConversion,
    {
        let bytes = Units::encode(acceleration, A::ACCELERATION_SCALE_FACTOR);
        Units::Distance(bytes)
    }

    /// Consumes the [`Units`] enum, returning real-world units (millimeters and seconds) using the
    /// appropriate [`scale factor`][1].
    ///
    /// [1]: UnitConversion
    pub(crate) const fn decode<A>(&self) -> f64
    where
        A: UnitConversion,
    {
        match self {
            Units::Distance(d) => i32::from_le_bytes(*d) as f64 / A::DISTANCE_ANGLE_SCALE_FACTOR,
            Units::Velocity(v) => i32::from_le_bytes(*v) as f64 / A::VELOCITY_SCALE_FACTOR,
            Units::Acceleration(a) => i32::from_le_bytes(*a) as f64 / A::ACCELERATION_SCALE_FACTOR,
        }
    }

    /// Returns `True` if [`self`][1] and [`other`][1] are equivalent within three decimal places.
    ///
    /// [1]: Units
    pub(crate) const fn approx<A>(&self, other: f64) -> bool
    where
        A: UnitConversion,
    {
        (self.decode::<A>() - other).abs() < 0.001
    }
}

impl Deref for Units {
    type Target = [u8; 4];

    fn deref(&self) -> &Self::Target {
        match self {
            Units::Distance(distance) => distance,
            Units::Velocity(velocity) => velocity,
            Units::Acceleration(acceleration) => acceleration,
        }
    }
}

impl IntoIterator for Units {
    type IntoIter = std::array::IntoIter<u8, 4>;
    type Item = u8;

    fn into_iter(self) -> Self::IntoIter {
        match self {
            Units::Distance(bytes) => IntoIterator::into_iter(bytes),
            Units::Velocity(bytes) => IntoIterator::into_iter(bytes),
            Units::Acceleration(bytes) => IntoIterator::into_iter(bytes),
        }
    }
}

/// # Thorlabs "Device Units" Explained
///
/// Internally, thorlabs devices use an encoder to track of their current position. All distances
/// must therefore be converted from real-word units (millimeters) to encoder-counts using the
/// correct scaling factor. This scaling factor may differ between device types due to different
/// encoder resolutions and gearing ratios.
///
/// The device's unit of time is determined by the encoder polling frequency. All time-dependent
/// units (e.g. velocity and acceleration) must therefore be converted from real-word units
/// (seconds) to device units using the correct scaling factor. This scaling factor may differ
/// between device types due to different encoder polling frequencies.
pub(crate) trait UnitConversion {
    const ACCELERATION_SCALE_FACTOR: f64;
    const DISTANCE_ANGLE_SCALE_FACTOR: f64;
    const VELOCITY_SCALE_FACTOR: f64;
}
