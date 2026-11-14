import type {Metadata} from "next"; import "./globals.css";
export const metadata:Metadata={title:"Receptionist Console",description:"Local-first AI receptionist"};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}