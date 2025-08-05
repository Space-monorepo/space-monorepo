import { API_URL } from "@/config";
import axios from "axios";

const axiosInstance = axios.create({
  baseURL: API_URL, // Endereço do seu backend
  timeout: 10000, // Tempo de espera para a requisição
});

export default axiosInstance;