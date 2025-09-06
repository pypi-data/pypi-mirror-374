// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::path::Path;

use anyhow::{ensure, Context, Result};
use mmap_rs::{Mmap, MmapFlags, MmapMut};
use thiserror::Error;

#[derive(Error, Debug, PartialEq, Eq, Hash, Clone)]
#[error("Accessed table index {index} out of {len}")]
pub struct OutOfBoundError {
    pub index: usize,
    pub len: usize,
}

pub struct Table<const ITEM_SIZE: usize, B> {
    data: B,
}

impl<const ITEM_SIZE: usize> Table<ITEM_SIZE, MmapMut> {
    /// Creates a new `.bin` file of the needed size
    pub fn new<P: AsRef<Path>>(path: P, num_nodes: usize) -> Result<Self> {
        let path = path.as_ref();
        let file_len = (num_nodes * ITEM_SIZE)
            .try_into()
            .context("File size overflowed u64")?;
        let file = std::fs::File::options()
            .read(true)
            .write(true)
            .create_new(true)
            .open(path)
            .with_context(|| format!("Could not create {}", path.display()))?;

        // fallocate the file with zeros so we can fill it without ever resizing it
        file.set_len(file_len)
            .with_context(|| format!("Could not fallocate {} with zeros", path.display()))?;

        let data = unsafe {
            mmap_rs::MmapOptions::new(file_len as _)
                .context("Could not initialize mmap")?
                .with_flags(MmapFlags::TRANSPARENT_HUGE_PAGES | MmapFlags::SHARED)
                .with_file(&file, 0)
                .map_mut()
                .with_context(|| format!("Could not mmap {}", path.display()))?
        };

        Ok(Self { data })
    }
}

impl<const ITEM_SIZE: usize> Table<ITEM_SIZE, Mmap> {
    /// Load a `.bin` file
    pub fn load<P: AsRef<Path>>(path: P) -> Result<Self> {
        let path = path.as_ref();
        let file_len = path
            .metadata()
            .with_context(|| format!("Could not stat {}", path.display()))?
            .len();
        ensure!(
            file_len % (ITEM_SIZE as u64) == 0,
            "Expected {} length to be a multiple of {}, but it is {}",
            path.display(),
            ITEM_SIZE,
            file_len
        );
        let file = std::fs::File::open(path)
            .with_context(|| format!("Could not open {}", path.display()))?;
        let data = unsafe {
            mmap_rs::MmapOptions::new(file_len as _)
                .context("Could not initialize mmap")?
                .with_flags(MmapFlags::TRANSPARENT_HUGE_PAGES | MmapFlags::RANDOM_ACCESS)
                .with_file(&file, 0)
                .map()
                .with_context(|| format!("Could not mmap {}", path.display()))?
        };
        Ok(Self { data })
    }
}
impl<const ITEM_SIZE: usize, B: AsRef<[u8]>> Table<ITEM_SIZE, B> {
    /// Convert a node_id to a SWHID
    #[inline]
    pub fn get(&self, index: usize) -> Result<[u8; ITEM_SIZE], OutOfBoundError> {
        let offset = index * ITEM_SIZE;
        let bytes = self
            .data
            .as_ref()
            .get(offset..offset + ITEM_SIZE)
            .ok_or(OutOfBoundError {
                index,
                len: self.data.as_ref().len() / ITEM_SIZE,
            })?;
        // this unwrap is always safe because we use the same const
        let bytes: [u8; ITEM_SIZE] = bytes.try_into().unwrap();
        Ok(bytes)
    }

    /// Return how many node_ids are in this map
    #[allow(clippy::len_without_is_empty)] // rationale: we don't care about empty maps
    #[inline]
    pub fn len(&self) -> usize {
        self.data.as_ref().len() / ITEM_SIZE
    }
}

impl<const ITEM_SIZE: usize, B: AsMut<[u8]> + AsRef<[u8]>> Table<ITEM_SIZE, B> {
    /// Set an item at the given position
    #[inline]
    pub fn set(&mut self, index: usize, item: [u8; ITEM_SIZE]) {
        let offset = index * ITEM_SIZE;
        self.data
            .as_mut()
            .get_mut(offset..offset + ITEM_SIZE)
            .expect("Tried to write past the end of table")
            .copy_from_slice(&item[..]);
    }
}
