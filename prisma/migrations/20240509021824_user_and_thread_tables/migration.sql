-- CreateTable
CREATE TABLE "FacebookUser" (
    "id" TEXT NOT NULL,
    "photo" TEXT,
    "gender" TEXT,
    "first_name" TEXT,
    "last_name" TEXT,
    "name" TEXT,
    "url" TEXT,

    CONSTRAINT "FacebookUser_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "FacebookThread" (
    "id" TEXT NOT NULL,
    "facebookUserId" TEXT NOT NULL,
    "otherFacebookUserId" TEXT NOT NULL,

    CONSTRAINT "FacebookThread_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "FacebookUser_id_key" ON "FacebookUser"("id");

-- CreateIndex
CREATE UNIQUE INDEX "FacebookThread_id_key" ON "FacebookThread"("id");

-- AddForeignKey
ALTER TABLE "FacebookThread" ADD CONSTRAINT "FacebookThread_facebookUserId_fkey" FOREIGN KEY ("facebookUserId") REFERENCES "FacebookUser"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "FacebookThread" ADD CONSTRAINT "FacebookThread_otherFacebookUserId_fkey" FOREIGN KEY ("otherFacebookUserId") REFERENCES "FacebookUser"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
