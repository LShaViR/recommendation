import { auth } from "@/lib/simulate-login";
import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

const AuthContext = createContext();

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const response = await auth();
        setToken(response.access_token);
      } catch (err) {
        console.error("Session expired");
      } finally {
        setLoading(false);
      }
    };
    initAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ token, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

// Custom hook for easy access
export const useAuth = () => useContext(AuthContext);
