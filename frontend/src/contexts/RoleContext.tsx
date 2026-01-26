import React, { createContext, useContext, useState } from "react";

const CONFIRMED_ROLE_STORAGE_KEY = "mercury:confirmedRoleId";

type RoleContextValue = {
  confirmedRoleId: string | null;
  setConfirmedRoleId: (roleId: string | null) => void;
};

const RoleContext = createContext<RoleContextValue | undefined>(undefined);

export const RoleProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [confirmedRoleId, setConfirmedRoleIdState] = useState<string | null>(() => {
    return localStorage.getItem(CONFIRMED_ROLE_STORAGE_KEY);
  });

  const setConfirmedRoleId = (roleId: string | null) => {
    setConfirmedRoleIdState(roleId);
    if (roleId) {
      localStorage.setItem(CONFIRMED_ROLE_STORAGE_KEY, roleId);
    } else {
      localStorage.removeItem(CONFIRMED_ROLE_STORAGE_KEY);
    }
  };

  return (
    <RoleContext.Provider value={{ confirmedRoleId, setConfirmedRoleId }}>
      {children}
    </RoleContext.Provider>
  );
};

export const useConfirmedRole = () => {
  const ctx = useContext(RoleContext);
  if (!ctx) {
    throw new Error("useConfirmedRole must be used within RoleProvider");
  }
  return ctx;
};
