#
# Copyright (C) Eratos Group Pty Ltd and its affiliates.
#
# This file was created as part of:
#
#   Eratos Python SDK
#
# It is proprietary software, you may not:
#
#   a) redistribute it and/or modify without permission from Eratos Group Pty Ltd.
#   b) reuse the code in part or in full without permission from Eratos Group Pty Ltd.
#
# If permission has been granted for reuse and/or redistribution it is subject
# to the following conditions:
#
#   a) The above copyright notice and this permission notice shall be included
#      in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import os
import base64
import hashlib
import logging
import pprint
import binascii
import urllib

_logger = logging.getLogger(__name__)

def move_prefix_to_new_format(content):
  ch_content = {}
  for k in content.keys():
    if k[0] == '$':
      _logger.warn('deprecated use of $ prefixes, move to @')
      if k == '$schema':
        nk = '@type'
      else:
        nk = '@' + k[1:]
      ch_content[nk] = content[k]
    else:
      ch_content[k] = content[k]
  return ch_content

def decode_request_content_response(req):
  ct = req.headers.get('Content-Type')
  if ct == None:
    return req.content
  cta = ct.split(';')[0].lower()
  if cta == 'application/json':
    return req.json()
  elif cta == 'plain/text':
    return req.text()
  else:
    return req.content

def calc_filemap_from_chunk(manifest, chunk_idx):
  icl = []
  cur_chunk_pos = 0
  cur_chunk_count = 0
  for it in manifest['items']:
    if cur_chunk_pos+it['size'] > manifest['chunkSize']:
      # This file requires multiple chunks, start on a new
      # chunk if the current chunk position is not 0.
      if cur_chunk_pos != 0:
        cur_chunk_pos = 0
        cur_chunk_count += 1
      first_chunk = cur_chunk_count
      first_chunk_start = cur_chunk_pos
      cur_chunk_count += it['size'] // manifest['chunkSize']
      cur_chunk_pos = it['size'] % manifest['chunkSize']
    else:
      first_chunk = cur_chunk_count
      first_chunk_start = cur_chunk_pos
      cur_chunk_pos += it['size']
      if cur_chunk_pos == manifest['chunkSize']:
        cur_chunk_pos = 0
        cur_chunk_count += 1
    last_chunk = cur_chunk_count
    last_chunk_end = cur_chunk_pos
    if cur_chunk_pos == 0:
      last_chunk -= 1
      last_chunk_end = manifest['chunkSize']
    
    if chunk_idx >= first_chunk and last_chunk > chunk_idx:
      icl += [{
        'item': it,
        'file_start': (chunk_idx - first_chunk) * manifest['chunkSize'],
        'chunk_start': 0,
        'count': manifest['chunkSize']
      }]
    elif chunk_idx == last_chunk and first_chunk < chunk_idx:
      icl += [{
        'item': it,
        'file_start': (chunk_idx - first_chunk) * manifest['chunkSize'],
        'chunk_start': 0,
        'count': last_chunk_end
      }]
    elif chunk_idx == first_chunk and chunk_idx == last_chunk:
      icl += [{
        'item': it,
        'file_start': first_chunk_start + ((chunk_idx - first_chunk) * manifest['chunkSize']),
        'chunk_start': first_chunk_start,
        'count': last_chunk_end - first_chunk_start
      }]
  return icl

def calc_chunksize_from_filesize(file_size):
  '''
  Calculate the required chunk size from a given file size.
  '''
  size_in_mb = file_size // (1024*1024)
  est_merkle_size = ((max(size_in_mb, 1) * 2) - 1) * 64
  est_chunk_size_mb = max(est_merkle_size // (16*1024*1024), 1)
  return est_chunk_size_mb * (1024*1024)

def fill_chunk_hash(content, chunk_size):
  left = chunk_size - len(content)
  if left > 0:
    content += b'\x00' * left
  return content

def dataset_chunks(files, chunk_size):
  '''
  Output the chunks for a given dataset.
  '''
  chunk_pos = 0
  chunk_content = b''
  for fn in files:
    file_size = os.stat(fn['path']).st_size
    if chunk_pos != 0 and chunk_pos+file_size > chunk_size:
      yield fill_chunk_hash(chunk_content, chunk_size)
      chunk_content = b''
      chunk_pos = 0
    file_pos = 0
    with open(fn['path'], 'rb') as f:
      while True:
        chunk_left = chunk_size - chunk_pos
        file_left = file_size - file_pos
        if file_left > chunk_left:
          chunk_content += f.read(chunk_left)
          yield fill_chunk_hash(chunk_content, chunk_size)
          chunk_content = b''
          chunk_pos = 0
          file_pos += chunk_left
        else:
          chunk_content += f.read(file_left)
          chunk_pos += file_left
          break
  if len(chunk_content) > 0:
    yield fill_chunk_hash(chunk_content, chunk_size)


def hash_dataset_chunks(files, chunk_size):
  '''
  Output the hashlist based on the files and chunk size.
  '''
  return [hashlib.sha256(chunk).digest() for chunk in dataset_chunks(files, chunk_size)]

file_to_hash_size = [
  [10485760, 262144],
  [20971520, 524288],
  [41943040, 1048576],
  [83886080, 2097152],
  [167772160, 4194304],
  [335544320, 8388608],
  [671088640, 16777216]
]

def calc_best_chunk_size(files):
  total_size = 0
  for fn in files:
    total_size += os.stat(fn['path']).st_size
  for hs in file_to_hash_size:
    if total_size < hs[0]:
      return hs[1]
  return file_to_hash_size[-1][1]

def get_meta_items(files):
  abs_paths = [os.path.abspath(f['path']) for f in files]
  if len(abs_paths) == 1:
    cpath = os.path.dirname(abs_paths[0])
  else:
    cpath = os.path.commonpath(abs_paths)
  meta_files = []
  for fn in files:
    meta_files += [{
      **fn,
      'path': os.path.relpath(fn['path'], cpath),
      'size': os.stat(fn['path']).st_size
    }]
  return meta_files

def extract_pn_and_did(id):
  o = urllib.parse.urlparse(id)
  return o.netloc, os.path.basename(o.path)

class Merkle:
  '''
  Generate a Merkle tree using the passed hashes.
  '''
  def __init__(self, hashes):
    self.leaf_hashes = hashes
    self.build()

  def build(self):
    assert(self.leaf_hashes is not None and len(self.leaf_hashes) > 0)
    if len(self.leaf_hashes) == 1:
      plain_hash = hashlib.sha256()
      plain_hash.update(b'\x00')
      plain_hash.update(self.leaf_hashes[0])
      self.hash_levels = [[plain_hash.digest()]]
    else:
      hash_levels = [self.leaf_hashes]
      while True:
        level_cnt = len(hash_levels[0])
        if level_cnt == 1:
          break
        hash_level = []
        for i in range(0,level_cnt-1,2):
          plain_hash = hashlib.sha256()
          if len(hash_levels) == 1:
            plain_hash.update(b'\x00')
          else:
            plain_hash.update(b'\x01')
          plain_hash.update(hash_levels[0][i+0])
          plain_hash.update(hash_levels[0][i+1])
          hash_level += [plain_hash.digest()]
        if level_cnt % 2 == 1:
          hash_level += [hash_levels[0][level_cnt-1]]
        hash_levels = [hash_level] + hash_levels
      self.hash_levels = hash_levels

  def root(self):
    return self.hash_levels[0]

  def root_b64(self):
    return base64.b64encode(self.hash_levels[0][0]).decode('ascii')

  def root_hex(self):
    return binascii.hexlify(self.hash_levels[0][0]).decode('ascii')

  def pprint(self):
    for i in range(len(self.hash_levels)):
      print('Level %02d (%02d): %s' % (i, len(self.hash_levels[i]), pprint.pformat([binascii.hexlify(h).decode('ascii') for h in self.hash_levels[i]], width=1024*1024)))
