import React from 'react';

import { FileOrFolder } from '@/shared.types';
import { formatUnixTimestamp, formatFileSize } from '@/utils';

export default function OverviewTable({ file }: { file: FileOrFolder | null }) {
  return (
    <div className="w-full overflow-hidden rounded-lg border border-surface mt-4">
      <table className="w-full">
        <tbody className="text-sm">
          <tr className="border-b border-surface">
            <td className="p-3 border-b border-surface bg-surface-light text-sm text-foreground dark:bg-surface-dark font-medium">
              Type
            </td>
            <td className="p-3">
              {file ? (file.is_dir ? 'Folder' : 'File') : null}
            </td>
          </tr>
          <tr className="border-b border-surface">
            <td className="p-3 border-b border-surface bg-surface-light text-sm text-foreground dark:bg-surface-dark font-medium">
              Last modified
            </td>
            <td className="p-3">
              {file ? formatUnixTimestamp(file.last_modified) : null}
            </td>
          </tr>
          <tr className="border-b border-surface">
            <td className="p-3 border-b border-surface bg-surface-light text-sm text-foreground dark:bg-surface-dark font-medium">
              Size
            </td>
            <td className="p-3">
              {file ? (file.is_dir ? '—' : formatFileSize(file.size)) : null}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
