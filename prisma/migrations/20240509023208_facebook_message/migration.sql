-- AlterTable
ALTER TABLE "FacebookThread" ADD COLUMN     "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- CreateTable
CREATE TABLE "FacebookMessage" (
    "id" TEXT NOT NULL,
    "authorId" TEXT NOT NULL,
    "threadId" TEXT NOT NULL,
    "message" TEXT NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "folder" JSONB NOT NULL,

    CONSTRAINT "FacebookMessage_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "FacebookMessage_id_key" ON "FacebookMessage"("id");

-- AddForeignKey
ALTER TABLE "FacebookMessage" ADD CONSTRAINT "FacebookMessage_authorId_fkey" FOREIGN KEY ("authorId") REFERENCES "FacebookUser"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "FacebookMessage" ADD CONSTRAINT "FacebookMessage_threadId_fkey" FOREIGN KEY ("threadId") REFERENCES "FacebookThread"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
