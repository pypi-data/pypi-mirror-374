import React from 'react';
import { useOutletContext } from 'react-router';

import type { OutletContextType } from '@/layouts/BrowseLayout';
import { useFileBrowserContext } from '@/contexts/FileBrowserContext';
import FileBrowser from './ui/BrowsePage/FileBrowser';
import Toolbar from './ui/BrowsePage/Toolbar';
import RenameDialog from './ui/Dialogs/Rename';
import Delete from './ui/Dialogs/Delete';
import ChangePermissions from './ui/Dialogs/ChangePermissions';
import ConvertFileDialog from './ui/Dialogs/ConvertFile';
import RecentDataLinksCard from './ui/BrowsePage/Dashboard/RecentDataLinksCard';
import RecentlyViewedCard from './ui/BrowsePage/Dashboard/RecentlyViewedCard';
import NavigationInput from './ui/BrowsePage/NavigateInput';

export default function Browse() {
  const {
    setShowPermissionsDialog,
    togglePropertiesDrawer,
    toggleSidebar,
    setShowConvertFileDialog,
    showPermissionsDialog,
    showPropertiesDrawer,
    showSidebar,
    showConvertFileDialog
  } = useOutletContext<OutletContextType>();

  const { fileBrowserState } = useFileBrowserContext();

  const [showDeleteDialog, setShowDeleteDialog] = React.useState(false);
  const [showRenameDialog, setShowRenameDialog] = React.useState(false);

  return (
    <div className="flex flex-col h-full min-w-fit max-h-full">
      <Toolbar
        showPropertiesDrawer={showPropertiesDrawer}
        togglePropertiesDrawer={togglePropertiesDrawer}
        showSidebar={showSidebar}
        toggleSidebar={toggleSidebar}
      />
      <div
        className={`relative grow shrink-0 max-h-[calc(100%-55px)] flex flex-col overflow-y-auto px-2 ${!fileBrowserState.currentFileSharePath ? 'grid grid-cols-2 grid-rows-[60px_1fr] bg-surface-light gap-6 p-6' : ''}`}
      >
        {!fileBrowserState.currentFileSharePath ? (
          <>
            <div className="col-span-2">
              <NavigationInput location="dashboard" />
            </div>
            <RecentlyViewedCard />
            <RecentDataLinksCard />
          </>
        ) : (
          <FileBrowser
            showPropertiesDrawer={showPropertiesDrawer}
            togglePropertiesDrawer={togglePropertiesDrawer}
            setShowRenameDialog={setShowRenameDialog}
            setShowDeleteDialog={setShowDeleteDialog}
            setShowPermissionsDialog={setShowPermissionsDialog}
            setShowConvertFileDialog={setShowConvertFileDialog}
          />
        )}
      </div>
      {showRenameDialog ? (
        <RenameDialog
          showRenameDialog={showRenameDialog}
          setShowRenameDialog={setShowRenameDialog}
        />
      ) : null}
      {showDeleteDialog ? (
        <Delete
          showDeleteDialog={showDeleteDialog}
          setShowDeleteDialog={setShowDeleteDialog}
        />
      ) : null}
      {showPermissionsDialog ? (
        <ChangePermissions
          showPermissionsDialog={showPermissionsDialog}
          setShowPermissionsDialog={setShowPermissionsDialog}
        />
      ) : null}
      {showConvertFileDialog ? (
        <ConvertFileDialog
          showConvertFileDialog={showConvertFileDialog}
          setShowConvertFileDialog={setShowConvertFileDialog}
        />
      ) : null}
    </div>
  );
}
