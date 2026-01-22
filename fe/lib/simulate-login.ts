import axios from "axios";
import { BACKEND_URL } from "./config";

export const auth = async () => {
  try {
    const formData = new FormData();
    formData.append("username", "lucky@gmail.com");
    formData.append("password", "rathoreL");
    const token = await axios.post(
      `${BACKEND_URL}/api/v1/login/access-token`,
      formData,
    );
    return token.data;
  } catch (error) {
    throw new Error("authentication failed");
  }
};
