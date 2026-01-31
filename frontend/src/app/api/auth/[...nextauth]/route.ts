
import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";

const handler = NextAuth({
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID || "",
            clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
        }),
    ],
    callbacks: {
        async signIn({ user, account, profile }) {
            try {
                // Sync user with backend
                const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                const res = await fetch(`${baseUrl}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: user.name,
                        email: user.email,
                        image: user.image
                    })
                });

                if (!res.ok) {
                    console.error("Backend sync failed", res.status, await res.text());
                }
                return true;
            } catch (e) {
                console.error("Backend sync error", e);
                return true;
            }
        },
        async jwt({ token, account }) {
            if (account) {
                token.id_token = account.id_token;
            }
            return token;
        },
        async session({ session, token }) {
            // @ts-ignore
            session.id_token = token.id_token;
            return session;
        }
    },
    pages: {
        signIn: '/login',
    }
});

export { handler as GET, handler as POST };
